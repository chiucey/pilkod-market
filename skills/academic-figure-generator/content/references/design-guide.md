# Academic Figure Design Guide

## 1. Academic Figure Types and Design Specifications

### 1.1 Model Architecture Diagram

**Purpose**: Showcase the complete structure of neural networks or machine learning models

**Design Key Points**:
- Use rectangles for layers (Conv2D, Linear, LSTM, etc.)
- Use specific shapes for special operations (attention mechanisms as diamonds or special symbols)
- Arrows indicate data flow direction
- Label dimension changes between layers (e.g., 224×224×3 → 112×112×64)
- Color coding: encoder in blue tones, decoder in green tones, skip connections as red dashed lines

**Standard Symbols**:
- Conv layer: Rectangle + "Conv" label
- Pooling: Trapezoid or rectangle + "Pool"
- Attention: Diamond or special "🔷" symbol
- FC layer: Rectangle + "FC" or "Linear"
- Dropout/BatchNorm: Small triangles or dashed borders

### 1.2 Algorithm Flowchart

**Purpose**: Display the execution steps and decision flow of algorithms

**Design Key Points**:
- Start/End in rounded rectangles
- Processing steps in rectangles
- Decisions in diamonds
- Flow connected with arrows
- Maintain left-to-right or top-to-bottom reading order
- Key paths in dark colors, auxiliary paths in light colors

**Standard Symbols**:
- Start/End: Rounded rectangle
- Processing step: Rectangle
- Decision: Diamond
- Input/Output: Parallelogram
- Subroutine: Double-bordered rectangle

### 1.3 Data Flow Diagram

**Purpose**: Showcase data processing and transformation in systems

**Design Key Points**:
- Data sources as cylinders or罐 shapes
- Processing modules as rectangles
- Data storage as open rectangles (files) or cylinders (databases)
- Data flow as labeled arrows with data types
- Pipe symbols indicate data transformation

### 1.4 Network Diagram

**Purpose**: Showcase connections and topology between nodes

**Design Key Points**:
- Nodes as circles or uniform shapes
- Edges represent connections
- Different colors/line styles distinguish connection types
- Clusters enclosed with dashed lines
- Node size indicates importance

### 1.5 Comparison Results

**Purpose**: Visualize experimental results and performance comparisons

**Chart Type Selection**:
- Line chart: Time series or continuous changes
- Bar chart: Discrete comparisons
- Scatter plot: Correlation analysis
- Heatmap: Multi-dimensional data

### 1.6 System Framework

**Purpose**: Showcase the architecture and organization of complete systems

**Design Key Points**:
- Modular design with clear boundaries
- Interfaces and interactions labeled with arrows
- Hierarchical structure top-to-bottom or outside-to-inside
- User interface at upstream
- Backend data processing at downstream
- Unified visual language

### 1.7 Mathematical Visualization

**Purpose**: Showcase mathematical derivations, matrix operations, or formula flows

**Design Key Points**:
- Matrices as boxes with element grids
- Vectors as columns
- Operations labeled with arrows and symbols
- Dimension annotations at key positions
- Color-coded different variable types

## 2. Color Scheme Reference

### General Academic Colors
- **Primary**: #2563EB (Academic Blue)
- **Secondary**: #059669 (Success Green), #DC2626 (Alert Red)
- **Neutral**: #6B7280 (Gray), #F9FAFB (Light Gray Background)
- **Accent**: #7C3AED (Purple, for highlighting)

### Deep Learning Domain
- **Encoder**: #3B82F6 (Blue tones)
- **Decoder**: #F59E0B (Orange tones)
- **Attention**: #EC4899 (Pink tones)
- **Loss Function**: #EF4444 (Red tones)
- **Feature Maps**: #10B981 (Green tones)

### Classic Architecture Colors
- **ResNet**: Blue primary
- **Transformer**: Purple/Blue gradient
- **GAN**: Red-blue contrast
- **LSTM/GRU**: Green tones

## 3. Top Conference Style Reference

### NeurIPS / ICML Style
- Clean, minimal decoration
- Generous white space
- Clear font hierarchy
- Usually monochrome or single-tone

### CVPR / ICCV / ECCV Style
- Rich color coding
- Detailed technical annotations
- Clear component boundaries
- Blue primary common

### ACL / EMNLP Style
- NLP-specific symbols
- Sequence labeling visualization
- Attention heatmaps
- Tree structure representation

## 4. Common Errors to Avoid

1. **Over-decoration**: Avoid shadows, gradients, 3D effects
2. **Text too small**: Ensure labels remain readable after scaling
3. **Color chaos**: Limit to 3-5 primary colors
4. **Information overload**: Each figure expresses one core idea
5. **Inconsistency**: Use uniform visual language for similar elements
6. **Missing labels**: All non-obvious elements need annotations
