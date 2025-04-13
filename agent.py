import asyncio
from mcp_agent.core.fastagent import FastAgent

# Create the application
fast = FastAgent("Video Project Organizer")

@fast.agent(
    instruction="""You are a Video Project Organizer Agent that organizes media files.

YOUR GOAL:
Move ALL files from an ingest folder into a well-organized project structure.

PROJECT STRUCTURE TO CREATE:
IngestFolder/ProjectName/
  - Raw/Video/     (for .mp4, .mov, .avi files)
  - Raw/Audio/     (for .wav, .mp3, .aac files)
  - Assets/Images/ (for .jpg, .png files)
  - Assets/Music/  (for music files)
  - Exports/       (for final renders)

HOW TO WORK:
1. Ask for project name and ingest folder location
2. List all files in the ingest folder
3. Create project folder structure INSIDE the ingest folder
4. Move EACH file to its correct location
5. Verify no files remain in the top level
6. Provide a summary report

IMPORTANT RULES:
- Create all folders WITHIN the ingest folder
- Process EVERY single file
- Explain EACH step you're taking
- After each action, describe what you did and what you'll do next
- Continue until ALL files are moved and organized
""",
    servers=["fileutils"],
    human_input=True,
    model="claude-3-5-sonnet-20241022",
    use_history=True,
    # request_params={"temperature": 0.7}  # Very low temperature for consistent behavior
)
async def main():
    try:
        async with fast.run() as agent:
            await agent()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
