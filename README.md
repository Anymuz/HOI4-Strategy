# HOI4 Strategy Guides

This repository provides automation tools for processing Hearts of Iron IV strategy guides. It contains utilities for converting JSON strategy data into well-formatted markdown guides and checklists, with built-in quality control and automation workflows.

## Features

- **JSON to Markdown Conversion:** Transform structured JSON strategy data into readable guides
- **Automated Checklist Generation:** Create actionable checklists from strategy guides  
- **Character Encoding Fix:** Clean up encoding issues in JSON files
- **CI/CD Pipeline:** Automated processing via GitHub Actions
- **Quality Control:** Schema validation for consistent guide structure

## Usage with Custom GPT

You can use a custom ChatGPT to generate JSON strategy guides that work with this repository's automation tools. The JSON structure is predefined by the schema and rules - simply request the country and strategy you want:

### Example Prompts

**Basic Country Strategy:**
```
Generate a strategy guide for Germany focusing on rapid expansion in Europe
```

**Specific Approach:**
```
Create a fascist Argentina guide focusing on South American domination and naval expansion
```

**Alternative Path:**
```
Generate a democratic United States guide emphasizing industrial buildup and late-war intervention
```

**Focus Tree Strategy:**
```
Create a guide for Japan prioritizing the Army focus tree and continental expansion over naval doctrine
```

The custom GPT will automatically generate properly structured JSON following the established schema, which can then be processed through this repository's automation pipeline to create formatted guides and checklists.

## Automation Workflow

The repository uses a 3-step automation pipeline:

1. **Character Cleaning** (`fix_json_characters.py`) - Fixes encoding issues in JSON files
2. **Guide Generation** (`json_to_markdown.py`) - Converts JSON to formatted markdown
3. **Checklist Creation** (`json_to_checklist.py`) - Generates actionable checklists

### CI/CD Pipeline

GitHub Actions automatically processes files when JSON guides are added to the `data/` directory:
- Validates JSON structure against schema
- Generates markdown guides
- Creates corresponding checklists
- Commits results to repository

## Repository Structure

This repository is organized into a clear directory structure that supports both manual and automated content generation:

```
HOI4-Strategy/
├── .github/
│   ├── workflows/                 # CI/CD automation
│   └── scripts/                   # Processing utilities
│       ├── fix_json_characters.py
│       ├── json_to_markdown.py
│       └── json_to_checklist.py
├── checklists/                    # Generated checklist outputs
├── guides/                        # Generated guide outputs  
├── data/                          # Input JSON files
├── schema.json                    # JSON schema validation
├── guide.md                       # Example output
├── argentina_fascist_1.17.md     # Example country guide
├── WORKFLOW.md                    # Detailed automation guide
└── README.md                      # This file
```

## Getting Started

1. Clone this repository
2. Add JSON strategy files to the `data/` directory
3. Run the automation scripts or push to trigger CI/CD
4. Find generated guides in `guides/` and checklists in `checklists/`

The automation tools ensure consistent formatting and quality across all generated strategy documentation.



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

**NOTE**: Pull Requests are welcome but will only be accepted after an in-game play testing, and since I dont have time to play video games all day every day this will be done on an ad-hoc first-come-first-serve basis. However if you wish to make use of the custom GPT to generate guides and then use the automation from this repo to produce a gameplay checklist then you may clone this repo as you please.
