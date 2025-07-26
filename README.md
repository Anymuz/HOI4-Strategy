# HOI4 Strategy Guides

This repository contains AI generated strategy guides and walkthrough content for Hearts of Iron IV.

## About

This is a collection of Markdown files containing strategic insights, tips, and guides for Hearts of Iron IV gameplay.

Soon there will be a custom chatGPT that you can use on their platform to produce these guides and the final response can be copied and pasted straight to an `.json` file for your pull request. The [workflow](WORKFLOW.md) will handle the rest.

## Repository Structure

This repository is organized into a clear directory structure that supports both manual and automated content generation:

```
/
├── data/                           # Input JSON files
│   └── *.json                      # Strategy guide data files
├── guides/                         # Generated Markdown guides  
│   └── *.md                        # Human-readable strategy guides
├── checklists/                     # Generated actionable checklists
│   └── *-checklist.md              # Interactive gameplay checklists
├── .github/                        # Automation infrastructure
│   ├── scripts/                    # Python conversion scripts
│   │   ├── fix_json_characters.py  # JSON character cleaning
│   │   ├── json_to_markdown.py     # Guide generation
│   │   ├── json_to_checklist.py    # Checklist creation
│   │   └── README.md               # Script documentation
│   └── workflows/                  # GitHub Actions automation
│       └── convert-json-guides.yml # Main conversion workflow
├── WORKFLOW.md                     # Automation workflow guide
├── schema.json                     # JSON format specification
└── README.md                       # This file
```

### Directory Explanations

#### `/data/` - Source Files
The heart of the content creation system. Place your strategy guide JSON files here to trigger automatic processing. Files must follow the established JSON schema (see `schema.json`).

**Example**: `argentina_fascist.json` → Triggers automatic generation of guide and checklist

#### `/guides/` - Generated Strategy Guides  
Auto-generated, human-readable Markdown guides optimized for reading and reference. These include:
- Clean formatting with proper tables and sections
- Cross-links to corresponding checklists
- Tier-based organization and metadata
- Special handling for complex sections (Air & Navy, Factory swaps, etc.)

#### `/checklists/` - Interactive Gameplay Checklists
Auto-generated actionable checklists optimized for in-game use. Features include:
- Interactive checkboxes for progress tracking
- Simplified, action-oriented formatting  
- Cross-links back to full strategy guides
- Special handling for complex timelines

#### `/.github/` - Automation Infrastructure
Contains all the automation scripts and workflows that power the conversion system:
- **Scripts**: Python tools for JSON cleaning, guide generation, and checklist creation
- **Workflows**: GitHub Actions that automatically process new JSON files

### How It Works

1. **Add JSON File**: Place a strategy guide JSON file in `/data/`
2. **Automatic Processing**: GitHub Actions automatically:
   - Cleans problematic Unicode characters from the JSON
   - Generates a readable Markdown guide in `/guides/`
   - Creates an interactive checklist in `/checklists/`
   - Cross-links both files for easy navigation
3. **Ready to Use**: Both the guide and checklist are automatically committed back to the repository

For detailed workflow information, see [WORKFLOW.md](WORKFLOW.md).



## Guides

This repo is under development and there is lots yet to be added including an automatic table of contents for the guides and a link to a custom GPT on chatGPT that can be used to create the  `.json` guides. When comitted via git to the /data folder a workflow is triggered that will handle the bad characters that GPT's like to use, and produce not only a markdown guide of tables but also an acompanying checklist to tick off while playing.

Remember AI makes mistakes, these guides may lead to defeat in game rather than victory, the purpose is to push current LLM's to the limit but of course no reason a human cannot write guides. And I hope to eventually build a tool that allows people to input their strategies into the `.json` format and host them here, but for now all the content is AI driven unlike my other work where AI is used purely as a productivity tool and assisant. 

## Disclaimer
I want to stress that this content is for a game developed and owned by paradox interactive whom I am not affiliated with in any way, this content is **unofficial**.

## Support the Project
This repo can be seen as a standalone community project for game players to share and use strategies and walkthroughs use when playing the game so long as the `.json` file is generated correctly either with the GPT variant under construction or any other tool to produce. This repo also serves as a knowledge base for use in various other projects involving AI-driven content.

I do not wish to take donations for this specific repo alone, its meerly a library, Hearts of Iron 4 is a game about war, and although to us players its all numbers and images, the reality of war is it affects lives and has real suffering. So instead anyone wishing to donate should use that money and donate to a charity that will help veterans and/or refugees of conflict, people who have had to go through the worse that humanity has to offer, instead of donating it to me just for playing a game and having a bit of fun with AI while at it.

## Contributing

Feel free to add new guides or improve existing ones by creating new `.json` files in the `/data/` directory and making a pull request. They must follow the structural layout and format defined in `schema.json` and be accurate to the game version, DLCs and Mods they are made for.

### How to Contribute

1. **Create JSON File**: Write your strategy guide in JSON format following the schema
2. **Place in `/data/`**: Add your `strategy_name.json` file to the `/data/` directory  
3. **Submit Pull Request**: The automation will handle generating the Markdown guide and checklist
4. **Review Process**: Guides will be play-tested before acceptance

**NOTE**: Pull Requests are welcome but will only be accepted after an in-game play testing, and since I dont have time to play video games all day every day this will be done on an ad-hoc first-come-first-serve basis. However if you wish to make use of the custom GPT to generate guides and then use the automation from this repo to produce a gameplay checklist then you may fork as you please.
