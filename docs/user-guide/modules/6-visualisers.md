# 🌇 Visualisers: Painting the City with Data

`Visualisers` in `UrbanMapper` are your go-to tools for turning raw numbers into stunning maps that reveal the hidden
stories of the city. Whether you’re zooming into `interactive` maps or crafting `polished static images` for a paper, we’ve
got you covered. Let’s dive in and explore how to bring your data to life! 😊

!!! question "Why Visualisers Rock ?"
    `Maps` don’t just display data—they make it speak. `Visualisers` through `UrbanMapper` help you uncover trends, spot outliers, and share insights with flair. Trust us, your spreadsheets will thank you.

## 🗺️ Types of Visualisers

`UrbanMapper` serves up two awesome flavors of visualisers, each with their pros and cons:

- [x] **Interactive Visualiser** 🖱️  
  Powered by `Folium`, these maps are all about exploration. `Zoom`, `pan`, and `click` to your heart’s content—perfect for presentations or digging into data hands-on.  
  - Zoom and pan like a pro  
  - Pop-up info on hover or click  
  - Pick from cool basemaps  
  - Color-code numeric data for instant insights  
  - Visualise more than one enriched attributes of interest

- [x] **Static Visualiser** 🖼️  
  Built with `Matplotlib`, these are your high-quality, no-_fuss_ maps. Ideal for reports, publications, or whenever you need a sharp snapshot.  
  - Crisp, customisable images  
  - Tweak colors, lines, and more  
  - Add legends and scale bars  
  - Export as `PNG`, `PDF`, `SVG`, you name it  

---

## 🏗️ Instantiate your first Visualisers

Getting started is a breeze with `UrbanMapper`’s factory pattern. Here’s how to whip up your visualisers:

### `Interactive Visualiser`

Craving a map you can play with? Check this out:

```python
import urban_mapper as um

interactive_vis = (
    um.UrbanMapper()
    .visual
    .with_type("Interactive")
    .with_style({"tiles": "CartoDB dark_matter"})
    .build()
)
```

**What’s happening here?**:  

  - `with_type("Interactive")`: Picks the `interactive` mode.  
  - `with_style({"tiles": "CartoDB dark_matter"})`: Sets a sleek dark basemap.
  - `build()`: Locks it in and hands you a ready-to-go visualiser.  

### Static Visualiser

Need something picture-perfect? Here’s the static version:

```python
static_vis = (
    um.UrbanMapper()
    .visual
    .with_type("Static")
    .with_style({"figsize": (10, 8), "cmap": "viridis"})
    .build()
)
```

**What’s happening here?**:  

  - `with_type("Static")`: Goes for the static option.  
  - `with_style({"figsize": (10, 8), "cmap": "viridis"})`: Sets the size and a vibrant color map.  
  - `build()`: Builds your visualiser, good to go.  

---

## 🎨 Configuring Visualisers

Want to make it your own? Both visualisers let you tweak the style with the `with_style` method. Here’s the rundown:

### Interactive Style Options

- `tiles`: Choose your basemap vibe (e.g., "OpenStreetMap", "Stamen Terrain").  
- `zoom_start`: Set the starting zoom (default: 10).  
- `width` & `height`: Size it up (e.g., "100%", 500 pixels).  
- `colormap`: Pick a color scheme (e.g., "YlOrRd").  
- `legend`: Toggle the legend on or off (default: True).  

### Static Style Options

- `figsize`: Set dimensions as a tuple (e.g., (10, 6)).  
- `cmap`: Select your color map (e.g., "viridis").  
- `linewidth`: Adjust line thickness (default: 1.0).  
- `alpha`: Play with transparency (0 to 1, default: 0.7).  
- `dpi`: Control resolution (default: 100).  

More to be seen in the `API` ref.

## 📊 Visualising Data

Visualisers shine brightest when they turn your data into maps. Here’s how to do it:

### In a Pipeline

Weave a visualiser into your workflow like this:

```python
from urban_mapper.pipeline import UrbanPipeline

pipeline = UrbanPipeline([
    # ... All previous components ...
    ("visualiser", interactive_vis)
])

mapped_data, enriched_layer = pipeline.transform()
fig = pipeline.visualise(["pickup_count"])
```

### Directly

For a quick peek, use a visualiser standalone:

```python
fig = interactive_vis.visualise(enriched_layer.get_layer(), column="pickup_count")
```

### Multiple Columns

Compare metrics side by side:

```python
fig = pipeline.visualise(["pickup_count", "avg_fare"])
```

- **Cool perk**: You’ll get toggle controls to flip between layers—perfect for spotting / comparing differences.  

–––

[Wants to know more? See this Feature Request :fontawesome-brands-python:](https://github.com/VIDA-NYU/UrbanMapper/issues/9){ .md-button }
