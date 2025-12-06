# Analysis Framework Flowchart

This flowchart visualizes the five-layer architecture for Telegram Quranic discourse analysis described in `agents/plans/AGENTS_ROADMAP.md`.

```mermaid
flowchart TB
    %% Layer 1: Data Layer - Foundations
    subgraph L1["Layer 1: Data Layer - Foundations"]
        direction TB
        RAW[Raw Telegram Data<br/>Messages, Channels, Reactions]
        MSG[Messages<br/>text, timestamp, channel_id]
        CHAN[Channels<br/>id, name/title]
        REACT[Reactions<br/>emoji tone, counts]
        ENRICH[Enriched Fields<br/>verse_id, ideals, sentiment,<br/>geo_tag, topic_cluster]

        RAW --> MSG
        RAW --> CHAN
        RAW --> REACT
        MSG --> ENRICH
        CHAN --> ENRICH
        REACT --> ENRICH
    end

    %% Five-Axis Tensor
    TENSOR[Five-Axis Tensor<br/>Verse × Ideal × Channel × Time × Sentiment]
    ENRICH --> TENSOR

    %% Layer 2: Derived Metrics Layer
    subgraph L2["Layer 2: Derived Metrics Layer - Research-Ready Aggregates"]
        direction TB
        AGG[Aggregation Engine<br/>Rolling windows, Statistical computation]
        VF[Verse Frequency<br/>Citations per channel per time]
        ID[Ideal Distribution<br/>Fractional composition]
        ST[Sentiment Trend<br/>Average sentiment over time]
        ENT[Diversity Entropy<br/>Shannon entropy measures]
        JSON[Versioned JSON Output<br/>Metrics snapshots with metadata]

        AGG --> VF
        AGG --> ID
        AGG --> ST
        AGG --> ENT
        VF --> JSON
        ID --> JSON
        ST --> JSON
        ENT --> JSON
    end

    TENSOR --> AGG

    %% Layer 3: Analytical Frameworks
    subgraph L3["Layer 3: Analytical Frameworks"]
        direction TB

        subgraph RETRO["A. Retrospective Study"]
            RET[Validation of Past Signals<br/>5 Hypotheses Testing]
            INSIGHTS[Retrospective Insights JSON<br/>Confidence intervals, z-scores, effect sizes]
            RET --> INSIGHTS
        end

        subgraph EXPLORE["B. Exploratory Monitoring"]
            DASH[Interactive Dashboard<br/>Line charts, pie charts,<br/>heatmaps, word clouds]
            VISUAL[Visual Pattern Recognition<br/>Filtered by date, channel, ideal]
            DASH --> VISUAL
        end

        subgraph PREDICT["C. Predictive Pilot"]
            MODEL[Lightweight Models<br/>Logistic regression,<br/>Transformer embeddings]
            SIGNALS[Early-Warning Signals<br/>Attention flags with probabilities]
            MODEL --> SIGNALS
        end
    end

    JSON --> RET
    JSON --> DASH
    JSON --> MODEL

    %% Layer 4: Technical Stack
    subgraph L4["Layer 4: Technical Stack - Implementation"]
        direction LR
        EXTRACT[Extraction<br/>Python, regex,<br/>emoji parser]
        ENRICH2[Enrichment<br/>Lookup tables,<br/>heuristics]
        AGG2[Aggregation<br/>Pandas, SQL,<br/>DuckDB]
        SERIAL[Serialization<br/>JSON schema<br/>versioning]
        VIZ[Visualization<br/>React, D3,<br/>Plotly]
        FORECAST[Forecast<br/>Scikit-learn,<br/>Prophet]

        EXTRACT --> ENRICH2
        ENRICH2 --> AGG2
        AGG2 --> SERIAL
        SERIAL --> VIZ
        SERIAL --> FORECAST
    end

    %% Layer 5: Epistemic Frame
    subgraph L5["Layer 5: Epistemic Frame - Temporal Recursion"]
        direction TB
        PRIORS[Statistical Priors<br/>Baseline models from past]
        BASELINE[Learned Equilibrium<br/>Expected patterns]
        ANOMALY[Anomaly Detection<br/>Deviation alerts]

        PRIORS --> BASELINE
        BASELINE --> ANOMALY
        ANOMALY -.Feedback.-> PRIORS
    end

    INSIGHTS --> PRIORS
    SIGNALS --> ANOMALY

    %% Final Output
    OUTPUT[Predictive Signals & Early Warning Indicators<br/>Evolving barometer of ideological climate]

    VISUAL --> OUTPUT
    SIGNALS --> OUTPUT
    ANOMALY --> OUTPUT

    %% Styling
    classDef layer1 fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef layer2 fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef layer3 fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef layer4 fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef layer5 fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef tensor fill:#fff9c4,stroke:#f57f17,stroke-width:3px
    classDef output fill:#ffebee,stroke:#b71c1c,stroke-width:3px

    class RAW,MSG,CHAN,REACT,ENRICH layer1
    class AGG,VF,ID,ST,ENT,JSON layer2
    class RET,INSIGHTS,DASH,VISUAL,MODEL,SIGNALS layer3
    class EXTRACT,ENRICH2,AGG2,SERIAL,VIZ,FORECAST layer4
    class PRIORS,BASELINE,ANOMALY layer5
    class TENSOR tensor
    class OUTPUT output
```

## Legend

### Five Layers

1. **Layer 1 (Blue)** - Data Layer: Raw data collection and enrichment with semantic fields
2. **Layer 2 (Purple)** - Derived Metrics: Statistical aggregations and versioned metrics
3. **Layer 3 (Orange)** - Analytical Frameworks: Three parallel analytical approaches
4. **Layer 4 (Green)** - Technical Stack: Implementation technologies and processing pipeline
5. **Layer 5 (Pink)** - Epistemic Frame: Temporal recursion and self-improving feedback loop

### Key Nodes (25 Total)

**Layer 1 (5 nodes):** Raw Data → Messages → Channels → Reactions → Enriched Fields

**Layer 2 (5 nodes):** Aggregation Engine → Verse Frequency → Ideal Distribution → Sentiment Trend → Entropy → JSON

**Layer 3 (6 nodes):**
- Retrospective: Validation → Insights
- Exploratory: Dashboard → Visual Recognition
- Predictive: Models → Signals

**Layer 4 (6 nodes):** Extraction → Enrichment → Aggregation → Serialization → Visualization → Forecast

**Layer 5 (3 nodes):** Priors → Baseline → Anomaly Detection (with feedback loop)

### Central Organizing Principle

**Five-Axis Tensor (Yellow):** Verse × Ideal × Channel × Time × Sentiment

This tensor serves as the core data structure that connects raw enriched data to all analytical frameworks.

### Final Output (Red)

**Predictive Signals & Early Warning Indicators** - The system becomes an evolving barometer of ideological climate through temporal recursion.

## Flow Summary

1. Raw Telegram data is collected and enriched with semantic, geographic, and temporal metadata
2. Enriched data forms a five-dimensional tensor
3. Statistical aggregations produce versioned metrics
4. Three analytical frameworks process metrics in parallel:
   - Retrospective validation confirms past patterns
   - Exploratory dashboard enables visual monitoring
   - Predictive models generate early-warning signals
5. Technical stack implements the entire pipeline
6. Epistemic frame creates feedback loop: past patterns inform future baselines
7. System outputs actionable intelligence and anomaly alerts
