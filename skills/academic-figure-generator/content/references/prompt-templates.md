# Academic Figure Generation Prompt Template Library

## Deep Learning Domain

### Transformer Architecture
```
Professional academic diagram of Transformer architecture,
showing encoder-decoder structure with [N] layers each,
encoder: multi-head self-attention (blue boxes) followed by feed-forward network,
decoder: masked self-attention, cross-attention to encoder, feed-forward,
positional encoding shown as sinusoidal wave pattern,
multi-head attention displayed as [h] parallel attention units,
residual connections as curved arrows around each sublayer,
layer normalization as triangle symbols,
data flow from source embeddings (left) through encoder,
through cross-attention to target embeddings (right),
dimension annotations: d_model = [512], d_ff = [2048],
clean minimalist academic style, white background,
publication-quality, sharp edges, professional typography
```

### ResNet Residual Block
```
ResNet residual block architecture diagram,
main path: Conv3x3 -> BatchNorm -> ReLU -> Conv3x3 -> BatchNorm,
skip connection path: identity mapping or 1x1 conv if dimension changes,
residual addition shown with circled plus symbol,
dimensions shown as input H×W×C -> output H×W×C,
when dimensions change: dotted outline 1x1 conv with stride,
clean technical illustration, white background,
blue for main path, orange for skip connection,
publication-quality, labeled components, academic style
```

### GAN Architecture
```
Generative Adversarial Network architecture diagram,
left side: Generator network (G) taking random noise z ~ N(0,1),
noise vector as vertical array of random values,
Generator: dense layers or transposed convolutions (green boxes),
progressively increasing spatial dimensions shown,
output: generated sample G(z) as image placeholder,
right side: Discriminator network (D) taking real or fake image,
Discriminator: convolution layers (blue boxes) decreasing dimensions,
output: single sigmoid neuron with probability,
dashed line separating real/fake inputs,
backpropagation arrows showing adversarial training,
loss functions: L_G, L_D labeled,
professional academic diagram, white background, publication-quality
```

### LSTM Cell Structure
```
LSTM cell architecture diagram in academic style,
center: memory cell state (horizontal line, top to bottom),
gates shown as sigmoid functions (σ) with circles,
forget gate: sigmoid taking h_{t-1} and x_t, output to cell state,
input gate: sigmoid (i) and tanh (C~) gates combined,
cell state multiplication and addition operations shown,
output gate: sigmoid (o) multiplied by tanh of cell state,
peephole connections as dashed lines to gates,
element-wise operations marked with symbols,
input/output arrows labeled h_{t-1}, h_t, x_t, C_{t-1}, C_t,
color scheme: input in gray, gates in blue, cell state in purple,
clean minimalist style, white background, publication-quality
```

### CLIP Model Architecture
```
CLIP (Contrastive Language-Image Pre-training) architecture diagram,
left branch: Image Encoder (Vision Transformer variant),
image input with patch embedding grid,
transformer encoder blocks with [N] layers,
[CLS] token output, projection to embedding space,
right branch: Text Encoder (Transformer),
text input with tokenization shown,
transformer encoder blocks with [N] layers,
[EOS] token output, projection to embedding space,
both branches converging to shared embedding space,
similarity calculation as dot product matrix,
diagonal highlighted for matching pairs,
contrastive loss optimization indicated,
clean professional academic diagram, white background,
publication-quality, labeled components
```

## Computer Vision Domain

### FCN (Fully Convolutional Network)
```
Fully Convolutional Network for semantic segmentation,
input: RGB image (H×W×3) on left,
encoder path: series of conv + pooling layers,
feature maps progressively halving in size, doubling channels,
[conv1, pool1] -> [conv2, pool2] -> [conv3, pool3] -> [conv4, pool4] -> [conv5, pool5],
bottleneck at [conv5] with spatial dimensions H/32 × W/32,
decoder path: upconvolution (deconv) layers,
skip connections from encoder at matching scales,
concatenation shown with double arrows,
gradually upsampling: H/16 -> H/8 -> H/4 -> H/2 -> H,
final 1×1 conv to num_classes channels,
output: segmentation map with class colors,
clean academic diagram, blue encoder, green decoder,
white background, publication-quality
```

### YOLO Detection Framework
```
YOLO object detection architecture diagram,
input: image [608×608×3] (or [416×416]),
backbone network (e.g., Darknet-53 or CSPDarknet),
feature extraction layers shown as rectangles,
spatial dimensions labeled at each stage,
neck: Feature Pyramid Network (FPN) + PANet,
top-down FPN pathway with lateral connections,
bottom-up PAN pathway,
head: detection heads at multiple scales (small, medium, large),
each head: [1×1 conv] for bbox predictions,
anchor boxes shown as dotted rectangles,
output: feature maps with encoded predictions,
S×S grid for each scale, each cell predicting B boxes,
clean technical diagram, white background,
publication-quality, labeled components
```

### U-Net Medical Image Segmentation
```
U-Net architecture for biomedical image segmentation,
input image (left) with corresponding ground truth mask (right),
contraction path (encoder): 2 conv layers per block, then max pool,
dimensions: [572×572×1] -> [568×568×64] -> [284×284×64] -> ...,
expansion path (decoder): upconv, concatenation, 2 conv layers,
skip connections as horizontal arrows at each level,
bottleneck connecting encoder to decoder,
output: pixel-wise segmentation map,
green boxes: conv + BN + ReLU,
gray arrows: max pool, upconv
red arrows: copy and crop for skip connections,
output convolution: 1×1 conv to num_classes,
clean academic diagram, blue encoder, green decoder,
white background, publication-quality
```

## Natural Language Processing Domain

### BERT Model Architecture
```
BERT (Bidirectional Encoder Representations from Transformers),
input: sentence with [CLS] token at start, [SEP] at end,
tokenization shown as wordpiece/token embeddings,
three embeddings summed: token, position, segment embeddings,
embedding layer as combined input block,
transformer encoder blocks: [N] identical layers,
each layer: multi-head self-attention -> add & norm -> feed-forward -> add & norm,
multi-head attention expanded to show [H] heads,
feed-forward network: inner linear, GELU activation, outer linear,
output: contextualized embeddings for each token,
[CLS] token used for classification,
self-attention weights can be visualized as heatmaps,
clean professional diagram, white background,
blue for embeddings, purple for attention, green for FFN,
publication-quality, labeled components
```

### Seq2seq with Attention
```
Sequence-to-sequence model with attention,
left: Encoder LSTM (or Transformer encoder),
input tokens in embedding boxes,
bi-directional LSTM shown as forward/backward arrows,
hidden state aggregation at final timestep,
center: Attention mechanism (for attention-based models),
query from decoder hidden state,
keys and values from encoder outputs,
attention score calculation shown,
context vector as weighted sum,
right: Decoder LSTM (or Transformer decoder),
output tokens as shifted sequence,
autoregressive generation shown with loop arrow,
output projection to vocabulary,
beam search optionally indicated,
loss: cross-entropy between predictions and targets,
clean academic diagram, white background,
publication-quality, clear data flow
```

## Graph Neural Network Domain

### GCN (Graph Convolutional Network)
```
Graph Convolutional Network layer diagram,
left: input graph with N nodes,
adjacency matrix A shown as small grid,
node features as feature matrix X (N×F),
center: GCN layer computation,
message passing: each node aggregates from neighbors,
formula: H^{(l+1)} = σ(D^{-1/2}ÂD^{-1/2}H^{(l)}W^{(l)}),
computation graph shown for single node,
neighbor aggregation with 1/N normalization,
right: output node embeddings H^{(l+1)},
updated features for each node,
message arrows from neighbors to center node,
clean academic diagram, nodes as circles,
edges as lines, feature matrices as rectangles,
white background, publication-quality
```

### Graph Attention Network
```
Graph Attention Network (GAT) layer illustration,
input: graph with node features,
attention mechanism expanded view,
two interacting nodes with feature vectors,
attention coefficients: e_ij = LeakyReLU(a^T [Wh_i || Wh_j]),
attention weights shown as edge thickness/color,
multi-head attention: [K] parallel attention heads,
heads shown as separate computation paths,
outputs averaged or concatenated,
self-loops included,
attention score visualization as heatmap overlay,
clean academic diagram, white background,
publication-quality, detailed annotations
```

## Multimodal Learning Domain

### VQA (Visual Question Answering)
```
Visual Question Answering system architecture,
left top: input image (e.g., scene photograph),
left bottom: input question text ("How many dogs?"),
image branch: CNN encoder (e.g., ResNet or Faster R-CNN),
extract spatial features or object features,
question branch: text encoder (LSTM or Transformer),
encode question to feature vector,
fusion module in center:
- Early fusion: concatenate modalities
- Late fusion: element-wise operations
- Attention-based fusion: question attending to image regions,
attention weights shown as heatmap overlay on image,
output: answer generation or classification,
answer types: yes/no, number, text,
clean academic diagram, white background,
publication-quality, clear module boundaries
```

## Universal Templates

### Custom Architecture Diagram
```
Professional [Domain] architecture diagram for [Specific Model],
showing main components: [Component 1], [Component 2], [Component 3],
data flow from [Input] through [Processing] to [Output],
key innovations highlighted: [Innovation 1], [Innovation 2],
layer dimensions annotated throughout,
connections styled by type: data flow (solid arrow),
control flow (dashed arrow), optional (dotted),
module colors by function: [Color 1] for [Function A],
[Color 2] for [Function B], [Color 3] for [Function C],
clean minimalist academic style, white background,
publication-quality, sharp edges, professional typography,
labeled components, consistent visual language
```

### Process/Pipeline Diagram
```
Clean [Process/Pipeline] flowchart showing stages:
[Stage 1: Input] -> [Stage 2: Preprocessing] -> [Stage 3: Core Processing] ->
[Stage 4: Refinement] -> [Stage 5: Output],
each stage as rounded rectangle with internal steps,
decision points as diamonds with Yes/No branches,
data transformations shown with symbols,
parallel branches for concurrent processes,
error handling paths as alternative routes,
intermediate data formats annotated,
performance metrics at key stages (optional),
clean professional style, white background,
publication-quality, clear visual hierarchy
```

### Results Comparison Chart
```
Professional comparison visualization for [Experiment Name],
showing [Method A] vs [Method B] vs [Method C],
[chart type: bar chart / line plot / radar chart],
metrics on y-axis: accuracy, F1, latency, etc.,
methods distinguished by color with legend,
baseline as horizontal dashed line,
optimal values highlighted,
statistical significance indicated with symbols,
clean minimalist style, white background,
publication-quality, clear axis labels,
consistent color scheme across figures
```
