# 🌇 Pipeline Generators: Describe, Generate, Analyse!

Imagine telling `UrbanMapper` exactly what urban analysis you want, and watching it craft a pipeline for you—no coding required! 
With **Pipeline Generators**, this becomes reality. Powered by `Large Language Models (LLMs)`, this feature transforms 
your natural language descriptions into executable Python code for `UrbanMapper` pipelines.

## 🤖 How Pipeline Generators Work

The process is simple and intuitive:

1. **Describe**: Write your analysis idea in plain English (note we have not tried other languages, but it could be fun to try!).
2. **Generate**: An LLM (like GPT-4) converts your description into a working `UrbanMapper` pipeline.  
3. **Execute**: Run the generated code to analyse and visualise your urban data.  

It’s like having a coding assistant who understands your urban analysis goals!

---

## 🤑 Pre-requisites

Since `Pipeline Generators` currently rely on `OpenAI` models, you’ll need an `OpenAI API key`. Set it up as an environment variable:

```bash
export OPENAI_API_KEY="your_openai_api_key"
```

!!! question "How To Get Your API Key"
    - Sign up at [OpenAI](https://platform.openai.com/api-keys).  
    - Navigate to the `API` section.  
    - Generate and copy your key.  
    - Set it in your terminal or script.

## 🛠️ Using Pipeline Generators: `PLUTO Data Example`

Let’s dive into a practical example: analysing building data from the `PLUTO` dataset in `Downtown Brooklyn`, `New York City`. 
We’ll map it to `street intersections`, `calculate average floors per intersection`, clean the data, and visualise it 
on a dark-themed map. Similarly to what we've previously presented and done in previous user-guides.

### Step 1: Write Your Description

Start with a clear, detailed description of your analysis:

```python
# Our urban wish list
user_description = """
I’ve got PLUTO data at './pluto.csv', with 'longitude' and 'latitude' columns.

Map this to street intersections in Downtown Brooklyn, New York City, USA, using a 50-metre threshold.

Work out the average number of floors per intersection from the 'numfloors' column.

The data’s for all of NYC and might have missing coordinates, so (1) fill in the gaps and (2) filter it to the urban layer’s bounding box.

Show the results on an interactive dark-themed map.
"""
```

**What’s Included?**:

  - [x] **Data**: PLUTO dataset at `'./pluto.csv'` with `'longitude'`, `'latitude'`, and `'numfloors'`.  
  - [x] **Location**: Downtown Brooklyn, NYC, USA.  
  - [x] **Task**: Map data to intersections (50m threshold) and compute average floors.  
  - [x] **Cleaning**: Fill missing coordinates and filter to the urban layer’s bounding box.  
  - [x] **Output**: An interactive, dark-themed map.

### Step 2: Generate the Pipeline

Use `UrbanMapper` to turn your description into code:

```python
import urban_mapper as um
from IPython.display import Code

# Start UrbanMapper
mapper = um.UrbanMapper()

# Generate pipeline suggestion
suggestion = (
    mapper
    .pipeline_generator # From the pipeline_generator module
    .with_LLM("gpt-4") # With gpt-4 type of LLM
    .generate_urban_pipeline(user_description) # Generate the pipeline based on the user description previously instantiated
)
# print(suggestion)  # See what it suggests (without highlighting)!

# Display the suggestion while highlighting the code in the cell
Code(suggestion, language="python")
```

**What Happens?**:

  - The LLM (GPT-4) interprets your description.
  - It generates a Python script that includes all the necessary steps to create the pipeline.
  - The code is displayed in a readable format, ready for copy pasting in the next cell for execution.

## 🎛️ Choosing an LLM

Pick the model that suits your needs:

  - **`GPT4`**: Most accurate, great for complex tasks.  
  - **`GPT35Turbo`**: Faster and cheaper, ideal for simpler jobs.  
  - **`GPT4o`**: Balances speed and power.  

Example with GPT-4o:

```python
suggestion = mapper.pipeline_generator.with_LLM("GPT4o").generate_urban_pipeline(user_description)
```

### Adding Custom Instructions

Want specific features? Add instructions:

```python
instructions = """
Ensure the pipeline:
1. Uses a BoundingBoxFilter
2. Handles missing data with a SimpleGeoImputer
3. Creates an interactive dark-themed map
"""

suggestion = (
    mapper.pipeline_generator
    .with_LLM("GPT4")
    .with_custom_instructions(instructions)
    .generate_urban_pipeline(user_description)
)
```

---

## ✍️ Tips for Great Descriptions

To get the best pipeline, include:  
- **Data Source**: File path and column names.  
- **Geography**: Specific location.  
- **Analysis**: What to calculate or map.  
- **Cleaning**: How to handle messy data.  
- **Visualisation**: Desired output style.  

**Example**: Our `PLUTO description` is detailed, so the `LLM` can generate a precise pipeline.
