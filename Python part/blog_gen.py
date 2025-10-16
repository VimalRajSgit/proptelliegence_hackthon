import requests
import random
import time
from datetime import datetime, timedelta
from crewai import Agent, Task, Crew, Process, LLM
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.colors import HexColor

# API Keys
WEATHER_API_KEY = "f4ed27622e29484a8c342846251210"
GROQ_API_KEY = ""

CITIES = ["Chennai", "Delhi", "Bengaluru", "Mumbai", "Kolkata", "Hyderabad"]

# Initialize Groq LLM for CrewAI with retry settings
llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY,
    temperature=0.8,  # Higher for more creative, personal writing
    max_tokens=2000  # Increased for longer blog posts
)


def get_detailed_weather(city):
    """Fetch detailed weather + air quality data for a city"""
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city},India&aqi=yes"
    response = requests.get(url)
    data = response.json()

    weather = {
        'city': data['location']['name'],
        'region': data['location']['region'],
        'country': data['location']['country'],
        'local_time': data['location']['localtime'],
        'temp_c': data['current']['temp_c'],
        'feels_like_c': data['current']['feelslike_c'],
        'condition': data['current']['condition']['text'],
        'wind_kph': data['current']['wind_kph'],
        'humidity': data['current']['humidity'],
        'uv': data['current']['uv'],
        'aqi_us': data['current']['air_quality']['us-epa-index'],
        'pm2_5': data['current']['air_quality']['pm2_5'],
        'pm10': data['current']['air_quality']['pm10']
    }
    return weather


def get_monthly_weather_data(city):
    """Fetch weather data for the past 30 days"""
    weather_records = []

    for days_ago in [7, 14, 21, 30]:
        past_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        url = f"http://api.weatherapi.com/v1/history.json?key={WEATHER_API_KEY}&q={city},India&dt={past_date}"

        try:
            response = requests.get(url)
            data = response.json()

            day_data = data['forecast']['forecastday'][0]['day']
            weather_records.append({
                'date': past_date,
                'avg_temp_c': day_data['avgtemp_c'],
                'max_temp_c': day_data['maxtemp_c'],
                'min_temp_c': day_data['mintemp_c'],
                'avg_humidity': day_data['avghumidity'],
                'condition': day_data['condition']['text'],
                'max_wind_kph': day_data['maxwind_kph'],
                'total_precip_mm': day_data['totalprecip_mm']
            })
        except:
            continue

    return weather_records


def create_pdf_blog(blog_text, image_path, city, current_weather, monthly_data):
    """Create a beautiful Medium-style PDF blog with image"""
    filename = f"weather_blog_{city}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    # Create PDF with more breathing room
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=60,
        leftMargin=60,
        topMargin=50,
        bottomMargin=50,
    )

    story = []
    styles = getSampleStyleSheet()

    # Modern blog title style - larger, bolder
    title_style = ParagraphStyle(
        'BlogTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=HexColor('#1a1a1a'),
        spaceAfter=8,
        leading=34,
        fontName='Helvetica-Bold'
    )

    # Author/date style - smaller, subtle
    byline_style = ParagraphStyle(
        'Byline',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#888888'),
        spaceAfter=30,
        fontName='Helvetica'
    )

    # Blog body style - more relaxed, larger text
    blog_body_style = ParagraphStyle(
        'BlogBody',
        parent=styles['BodyText'],
        fontSize=12,
        textColor=HexColor('#1a1a1a'),
        spaceAfter=14,
        leading=20,
        fontName='Helvetica'
    )

    # Section heading - Medium-style (bold, not colored)
    blog_section_style = ParagraphStyle(
        'BlogSection',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=HexColor('#1a1a1a'),
        spaceAfter=10,
        spaceBefore=24,
        fontName='Helvetica-Bold'
    )

    # Caption style for image
    caption_style = ParagraphStyle(
        'Caption',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#666666'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    )

    # Quote/highlight style
    highlight_style = ParagraphStyle(
        'Highlight',
        parent=styles['Normal'],
        fontSize=13,
        textColor=HexColor('#2c3e50'),
        spaceAfter=16,
        leftIndent=30,
        rightIndent=30,
        fontName='Helvetica-Oblique',
        leading=20
    )

    # Extract title and clean it
    lines = [l.strip() for l in blog_text.strip().split('\n') if l.strip()]
    title = lines[0].replace('#', '').replace('*', '').strip() if lines else f"Weather Update: {city}"

    # Add title
    story.append(Paragraph(title, title_style))

    # Add byline
    byline = f"Weather Blog · {city}, India · {datetime.now().strftime('%B %d, %Y')}"
    story.append(Paragraph(byline, byline_style))

    # Horizontal line after header
    story.append(Spacer(1, 0.1 * inch))

    # Process content
    paragraph_count = 0
    image_added = False
    skip_next = False

    for i, line in enumerate(lines[1:], 1):
        if skip_next:
            skip_next = False
            continue

        line = line.strip()
        if not line or line in ['---', '***', '===']:
            continue

        # Clean line from markdown
        clean_line = line.replace('**', '').replace('*', '').replace('##', '').replace('#', '')

        # Check if it's a heading (starts with # or is very short and bold-looking)
        is_heading = line.startswith('#') or (len(line) < 60 and '**' in line and paragraph_count > 0)

        if is_heading:
            # Add image before a middle section (after 2-3 paragraphs)
            if not image_added and paragraph_count >= 2 and paragraph_count <= 4:
                story.append(Spacer(1, 0.3 * inch))
                try:
                    # Add image
                    img = RLImage(image_path, width=6 * inch, height=4 * inch)
                    story.append(img)
                    story.append(Spacer(1, 0.1 * inch))

                    # Caption
                    caption = f"The current weather scene in {city} | Photo: AI Generated"
                    story.append(Paragraph(caption, caption_style))
                    story.append(Spacer(1, 0.3 * inch))
                    image_added = True
                except Exception as e:
                    print(f"Could not add image: {e}")

            # Add section heading
            heading_text = clean_line.strip()
            story.append(Paragraph(heading_text, blog_section_style))
        else:
            # Regular paragraph
            # Check if it's a special callout or quote (italicized or indented content)
            if line.startswith('>') or line.startswith('•'):
                clean_line = clean_line.replace('>', '').replace('•', '').strip()
                story.append(Paragraph(clean_line, highlight_style))
            else:
                story.append(Paragraph(clean_line, blog_body_style))

            paragraph_count += 1

            # Add image in middle if not yet added (safety net)
            if not image_added and paragraph_count == 4:
                story.append(Spacer(1, 0.3 * inch))
                try:
                    img = RLImage(image_path, width=6 * inch, height=4 * inch)
                    story.append(img)
                    story.append(Spacer(1, 0.1 * inch))
                    caption = f"The current weather scene in {city} | Photo: AI Generated"
                    story.append(Paragraph(caption, caption_style))
                    story.append(Spacer(1, 0.3 * inch))
                    image_added = True
                except:
                    pass

    # If image still not added, add at end
    if not image_added:
        story.append(Spacer(1, 0.3 * inch))
        try:
            img = RLImage(image_path, width=6 * inch, height=4 * inch)
            story.append(img)
            story.append(Spacer(1, 0.1 * inch))
            caption = f"The current weather scene in {city} | Photo: AI Generated"
            story.append(Paragraph(caption, caption_style))
        except:
            pass

    # Add closing line
    story.append(Spacer(1, 0.4 * inch))
    closing_line = "─" * 60
    story.append(Paragraph(closing_line, caption_style))

    # Footer
    footer = f"""
    <i>Stay updated with daily weather insights and community observations.</i><br/>
    Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
    """
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph(footer, caption_style))

    # Build PDF
    doc.build(story)
    return filename


def generate_image(prompt):
    """Generate an AI image from Pollinations API"""
    url = f"https://image.pollinations.ai/prompt/{prompt}"
    response = requests.get(url)
    filename = "weather_image.png"
    with open(filename, "wb") as f:
        f.write(response.content)
    return filename


def create_weather_crew(city, current_weather, monthly_data):
    """Create a CrewAI crew with specialized agents"""

    # Prepare data strings
    monthly_summary = "\n".join([
        f"- {record['date']}: {record['avg_temp_c']}°C (High: {record['max_temp_c']}°C, Low: {record['min_temp_c']}°C), {record['condition']}, Humidity: {record['avg_humidity']}%, Rain: {record['total_precip_mm']}mm"
        for record in monthly_data
    ])

    current_summary = f"""
    City: {current_weather['city']}, {current_weather['region']}
    Temperature: {current_weather['temp_c']}°C (feels like {current_weather['feels_like_c']}°C)
    Condition: {current_weather['condition']}
    Humidity: {current_weather['humidity']}%
    Wind: {current_weather['wind_kph']} km/h
    UV Index: {current_weather['uv']}
    Air Quality Index (US EPA): {current_weather['aqi_us']}
    PM2.5: {current_weather['pm2_5']}, PM10: {current_weather['pm10']}
    """

    # Agent 1: Weather Data Analyst
    weather_analyst = Agent(
        role='Senior Weather Data Analyst',
        goal=f'Provide deep, insightful analysis of weather patterns for {city}, India with personal observations',
        backstory="""You are a veteran meteorologist with 20 years of experience 
        tracking Indian weather patterns. You've witnessed countless monsoons, heat waves, 
        and climate shifts. You have a knack for spotting patterns that others miss and 
        love sharing your observations with the community. You often reference specific 
        weather events you've tracked and their impact on daily life. You write in first 
        person, making your analysis personal and relatable.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # Agent 2: Air Quality Specialist
    air_quality_specialist = Agent(
        role='Air Quality & Public Health Specialist',
        goal=f'Provide practical, caring advice about air quality and health for {city} residents',
        backstory="""You are an environmental health scientist who has spent 15 years 
        monitoring air quality across Indian cities. You've seen firsthand how pollution 
        affects different communities. You're passionate about helping people protect 
        themselves and their families. You share real stories from your fieldwork and 
        give actionable, practical advice. You write with empathy and urgency, like 
        talking to a concerned neighbor.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # Agent 3: Content Writer
    content_writer = Agent(
        role='Weather Storyteller & Community Blogger',
        goal=f'Craft engaging, conversational weather stories that connect with {city} residents',
        backstory="""You are a local weather blogger who has been writing about {city}'s 
        weather for 10 years. You live in the city and experience the weather alongside 
        your readers. You have a talent for turning dry weather data into compelling 
        stories. You often start with personal anecdotes, use conversational language, 
        and address readers directly as "you" and "we". Your writing style is warm, 
        engaging, and feels like advice from a knowledgeable friend. You love using 
        specific examples and painting vivid pictures of weather conditions.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # Task 1: Analyze Weather Trends
    analyze_trends = Task(
        description=f"""As a meteorologist who has been tracking {city}'s weather for years, 
        analyze the current situation and share your observations with SPECIFIC DATA:

        CURRENT WEATHER:
        {current_summary}

        MONTHLY DATA (PAST 30 DAYS):
        {monthly_summary}

        Write a detailed analysis (300-350 words) that MUST include:
        1. **Last Week's Weather**: "Last week (around {monthly_data[0]['date']}), we saw temperatures averaging {monthly_data[0]['avg_temp_c']}°C with highs reaching {monthly_data[0]['max_temp_c']}°C. The weather was {monthly_data[0]['condition']} with {monthly_data[0]['total_precip_mm']}mm of rainfall."

        2. **Two Weeks Ago**: Compare with data from {monthly_data[1]['date']} - mention specific temperatures and conditions

        3. **Three Weeks Back**: Reference {monthly_data[2]['date']} data and how it differed

        4. **A Month Ago**: Compare with {monthly_data[3]['date']} - "Exactly a month ago on {monthly_data[3]['date']}, temperatures were at {monthly_data[3]['avg_temp_c']}°C..."

        5. **Temperature Progression**: "Over the past month, we've seen temperatures shift from {monthly_data[3]['avg_temp_c']}°C (30 days ago) to {monthly_data[0]['avg_temp_c']}°C (last week) to today's {current_weather['temp_c']}°C - that's a [calculate] degree change."

        6. **Rainfall Pattern**: Mention total rainfall across the dates: "Rainfall has been [pattern] with {monthly_data[0]['total_precip_mm']}mm last week, {monthly_data[1]['total_precip_mm']}mm two weeks ago..."

        7. **Humidity Trends**: Compare humidity levels across all dates

        8. **Your Expert Take**: "In my 20 years tracking {city}'s weather, this [month/pattern] reminds me of..."

        USE ACTUAL NUMBERS AND DATES. Make it data-rich but conversational.
        Write in FIRST PERSON.""",
        expected_output="A data-rich, personal weather analysis with specific dates, temperatures, and comparisons across the past month, written in first person with expert commentary",
        agent=weather_analyst
    )

    # Task 2: Air Quality Assessment
    assess_air_quality = Task(
        description=f"""As someone who has been monitoring air quality in {city} for years, 
        assess the current situation and give practical advice:

        Current AQI: {current_weather['aqi_us']} (US EPA Index)
        PM2.5: {current_weather['pm2_5']}
        PM10: {current_weather['pm10']}

        Write a caring, practical assessment (200-250 words) that includes:
        1. Start with "I've been monitoring {city}'s air quality for years, and here's what I'm seeing today..."
        2. Explain what these numbers actually mean for people's daily lives
        3. Share a specific example or story about how this level of pollution affects residents
        4. Give detailed, actionable advice for different groups (children, elderly, those with asthma)
        5. Recommend specific times of day to go outside or stay indoors
        6. Suggest practical solutions (masks, air purifiers, timing outdoor activities)
        7. Express genuine concern and empathy

        Write in FIRST PERSON, like you're talking to your neighbors. Use "you" and "we" frequently.
        Be warm but direct about health risks.""",
        expected_output="A personal, empathetic air quality assessment with specific health advice and practical recommendations, written in first person addressing readers directly",
        agent=air_quality_specialist
    )

    # Task 3: Write Blog Post
    write_blog = Task(
        description=f"""You're writing your weekly weather update for {city} residents. 
        Use the meteorologist's DATA-RICH observations and air quality specialist's advice.

        Requirements:
        - Write a compelling, personal title that hooks readers
        - Start with a relatable opening anecdote (2-3 sentences about the weather TODAY)
        - Introduction paragraph setting the scene with today's actual numbers

        - **"Looking Back: The Past Month in Numbers"** section:
          * Weave in ALL the specific data from the meteorologist
          * Last week's temps, two weeks ago, three weeks ago, a month ago
          * Use actual dates and numbers
          * Make comparisons: "We've gone from X°C to Y°C in just 30 days"
          * Include rainfall data across these periods

        - **"What I'm Seeing Today"** section:
          * Current conditions with specific numbers
          * How today compares to the weekly/monthly trends
          * Temperature: {current_weather['temp_c']}°C, Humidity: {current_weather['humidity']}%

        - **"Air Quality Reality Check"** section:
          * Current AQI: {current_weather['aqi_us']} with specific PM2.5 and PM10 numbers
          * Incorporate the specialist's advice
          * Compare air quality if data is available from past weeks

        - **"What This Means for Your Week"** section:
          * Practical advice based on the DATA and TRENDS
          * Not just generic tips - specific to this weather pattern
          * What to expect based on the progression we've seen

        - Engaging conclusion with forward-looking statement based on trends

        CRITICAL: Include LOTS OF SPECIFIC DATA:
        - Actual temperatures from each week
        - Specific dates when mentioned
        - Rainfall amounts
        - Humidity percentages
        - Temperature changes ("up 6 degrees from last week")
        - Comparisons with numbers

        STYLE:
        - 800-1000 words (Medium-length blog)
        - First person ("I", "we", "you")
        - Conversational but data-rich
        - Short paragraphs (2-4 sentences)
        - Balance personal storytelling with hard numbers
        - Like a weather-savvy friend sharing data over coffee

        Think: "Data-driven storytelling" not "dry weather report".""",
        expected_output="A comprehensive 800-1000 word blog with extensive specific data from the past month, personal narrative, current conditions analysis, and practical advice - all woven together conversationally",
        agent=content_writer,
        context=[analyze_trends, assess_air_quality]
    )

    # Create and return the crew with error handling
    crew = Crew(
        agents=[weather_analyst, air_quality_specialist, content_writer],
        tasks=[analyze_trends, assess_air_quality, write_blog],
        process=Process.sequential,
        verbose=True,
        max_rpm=10,  # Limit requests per minute
    )

    return crew


def run_crew_with_retry(crew, max_retries=3, delay=5):
    """Run crew with retry logic for handling API errors"""
    for attempt in range(max_retries):
        try:
            print(f"🔄 Attempt {attempt + 1}/{max_retries}...")
            result = crew.kickoff()
            return result
        except Exception as e:
            error_msg = str(e)
            if "InternalServerError" in error_msg or "500" in error_msg:
                if attempt < max_retries - 1:
                    print(f"⚠️  Groq API error (server busy). Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    print(f"❌ Failed after {max_retries} attempts. Using fallback...")
                    return generate_fallback_blog(crew)
            else:
                raise e
    return None


def generate_fallback_blog(crew):
    """Generate a simple blog without AI when API fails"""
    # Extract weather data from the crew's context
    tasks = crew.tasks
    task = tasks[0]
    description = task.description

    return f"""
Weather Update: Quick Summary

We're experiencing some technical difficulties with our AI blog generation system, 
but here's what you need to know about the current weather conditions:

{description[:500]}

For the most up-to-date weather information, please check your local weather service.
We apologize for the inconvenience and are working to restore full functionality.

Stay safe and weather-aware!
"""


def main():
    # Randomly choose a city
    city = random.choice(CITIES)
    print(f"\n{'=' * 70}")
    print(f"🌤️  WEATHER BLOG GENERATOR WITH CREWAI")
    print(f"{'=' * 70}")
    print(f"📍 Selected City: {city}\n")

    # Get weather + monthly data
    print("🔄 Fetching current weather data...")
    current = get_detailed_weather(city)

    print("🔄 Fetching monthly historical data (this may take a moment)...")
    monthly_data = get_monthly_weather_data(city)

    # Display raw weather data
    print(f"\n{'=' * 70}")
    print(f"📊 WEATHER DATA FOR {city.upper()}")
    print(f"{'=' * 70}")
    print(f"🌡️  Temperature: {current['temp_c']}°C (Feels like {current['feels_like_c']}°C)")
    print(f"💨 Wind: {current['wind_kph']} km/h")
    print(f"💧 Humidity: {current['humidity']}%")
    print(f"☀️  UV Index: {current['uv']}")
    print(f"🏭 AQI (US EPA): {current['aqi_us']} | PM2.5: {current['pm2_5']} | PM10: {current['pm10']}")
    print(f"☁️  Condition: {current['condition']}")

    print(f"\n📅 MONTHLY DATA SUMMARY:")
    for record in monthly_data:
        print(f"  {record['date']}: {record['avg_temp_c']}°C ({record['condition']})")

    # Create CrewAI agents and generate blog
    print(f"\n{'=' * 70}")
    print("🤖 INITIALIZING CREWAI AGENTS")
    print(f"{'=' * 70}")
    print("👨‍🔬 Agent 1: Weather Data Analyst")
    print("👩‍⚕️ Agent 2: Air Quality Specialist")
    print("✍️  Agent 3: Content Writer")
    print("\n⚙️  Starting collaborative blog generation...\n")

    crew = create_weather_crew(city, current, monthly_data)

    # Run with retry logic
    result = run_crew_with_retry(crew, max_retries=3, delay=5)

    # Display the blog
    print(f"\n{'=' * 70}")
    print("📝 GENERATED WEATHER BLOG POST")
    print(f"{'=' * 70}\n")
    print(result)
    print(f"\n{'=' * 70}")

    # Generate image
    print(f"\n🎨 Generating AI image...")
    prompt = f"{current['condition']} weather in {city}, India, realistic photo, high quality"
    image_path = generate_image(prompt)
    print(f"🖼️  Image saved as: {image_path}")

    # Display image in Colab
    try:
        from IPython.display import Image, display
        print("\n📷 Displaying image:")
        display(Image(filename=image_path))
    except:
        print("(Image display requires IPython environment)")

    # Create PDF blog
    print(f"\n📄 Creating professional PDF blog...")
    pdf_filename = create_pdf_blog(str(result), image_path, city, current, monthly_data)
    print(f"✅ PDF Blog created: {pdf_filename}")

    print(f"\n{'=' * 70}")
    print("✅ PROCESS COMPLETED SUCCESSFULLY!")
    print(f"{'=' * 70}")
    print(f"📄 PDF saved as: {pdf_filename}")
    print(f"🖼️  Image saved as: {image_path}")
    print(f"\n💡 Open the PDF to see your beautifully formatted weather blog!")
    print(f"{'=' * 70}\n")


# Run the system
if __name__ == "__main__":
    main()
