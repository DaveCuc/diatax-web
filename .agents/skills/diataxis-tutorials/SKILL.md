---
name: diataxis-tutorials
description: Builds a practical lesson focused on skill acquisition through directed action, guaranteeing a complete and successful learning experience (Tutorials pillar). Use this skill whenever the user requests a tutorial, a step-by-step learning guide, or wants to teach a new user how to start using their repository/code.
---

# Learning: Tutorials

Pragmatic and responsible instructor. The perspective uses the first-person plural ("we") to guide the process. Suppresses academic tone, prioritizing constant empirical reinforcement.

## Step-by-Step Instructions
* Extracts the main execution flow from the analyzed repository.
* Establishes a visible result from the beginning (e.g., "In this tutorial we will create...").
* Eliminates all theoretical explanation about underlying principles or abstractions; if the code uses a specific pattern, declare it as a fact without justifying it theoretically.
* Blocks alternatives: maps a single foolproof path and ignores secondary conditional branches.
* Includes continuous narrative markers describing the expected output after each console action or code execution.

## Required Variables or Data
| Variable | Technical Description |
| :--- | :--- |
| `[TARGET_OUTCOME]` | The tangible final product to build in the session (e.g., an active server, a rendered web component). |
| `[PREREQUISITES_ENV]` | Strictly necessary pre-installed system tools and instances. |
| `[CODE_PIPELINE]` | Immutable temporal sequence of files or functions to execute. |

## Output Example
> In this tutorial, we will create and deploy a single-instance web application. 
>
> Step 1: Initialization
> Execute the following command in your terminal to create the foundation block:
> $ init_project --start
>
> The command will return several lines of logs in your terminal indicating the creation of the logical folder structure. The final result will show: "Success: Project mounted".
>
> Step 2: Compilation
> Next, execute:
> $ build_project
>
> You will immediately notice that the /dist directory is generated. This directory must exist before proceeding to the deployment step.
