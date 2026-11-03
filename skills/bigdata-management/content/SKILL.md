---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: b81bcfd69838da03a49b20ee896b2cd9
    PropagateID: b81bcfd69838da03a49b20ee896b2cd9
    ReservedCode1: 3044022001ce38a7ea4fa31c98ec8a07a397370d01cb4997716e88b229798d515d805e5602201d644e8b57ffb12a3025eecdba8e938c3c35f724a081c92f627a04cde80f3197
    ReservedCode2: 3046022100e1cb8decfcaf66621eea73f2bee86f4ff0d35f38cb26473b8cca75491a1c7862022100e254c995b14553eb55a5c51c2f9cc8dc44d85b0f2a83ed7548b100691fbdef57
description: |-
    Provide professional guidance on big data management and applications, covering
    data collection, storage architecture, processing frameworks, analysis methods, and
    practical application scenarios. Use when user asks about data engineering,
    Hadoop ecosystem, data pipelines, data governance, data analysis, machine learning
    with big data, or designing big data solutions. Do NOT use for general programming
    questions unrelated to big data contexts.
name: bigdata-management
---

# Big Data Management and Applications

## Inputs to collect

- **Domain context**: Is this for learning/education, professional work, or project implementation?
- **Specific area**: Does the user focus on data collection, storage, processing, analysis, or application?
- **Tech stack preference**: Any specific tools or frameworks the user prefers (e.g., Hadoop, Spark, Flink)?
- **Problem type**: Is this a theoretical question, practical implementation, or solution design?

## Procedure

### Core Knowledge Areas

#### 1. Data Collection and Integration
- Real-time data collection: Flume, Kafka Connect, logstash
- Batch data ingestion: Sqoop, DataX, Kafka
- Data formats: JSON, CSV, Parquet, ORC, Avro
- Data validation and quality checks

#### 2. Storage Architecture
- Distributed file systems: HDFS, Ceph
- Data lakes: Delta Lake, Iceberg, Hudi
- NoSQL databases: HBase, MongoDB, Cassandra
- Time-series databases: InfluxDB, TimescaleDB
- Data warehouse: Hive, ClickHouse, StarRocks, Doris

#### 3. Processing Frameworks
- Batch processing: MapReduce, Spark SQL, Flink Batch
- Stream processing: Kafka Streams, Flink, Spark Streaming, Storm
- ETL pipelines: Airflow, DolphinScheduler, Azkaban
- Data transformation: Spark DataFrame, Flink Table API

#### 4. Analysis and Computing
- SQL engines: Presto, Trino, Hive LLAP, Spark Thrift Server
- OLAP engines: ClickHouse, Druid, Kylin, Doris
- Machine learning: Spark MLlib, XGBoost on Spark, TensorFlow on Spark
- Graph processing: GraphX, Neo4j, Gremlin

#### 5. Data Governance
- Data catalog: Apache Atlas, DataHub, OpenMetadata
- Data lineage: Apache Griffin, Great Expectations
- Data quality: Deequ, Great Expectations, Delta Lake schema enforcement
- Data security: Ranger, Sentry, column-level encryption

#### 6. Practical Application Scenarios
- Real-time data dashboard and monitoring
- User behavior analysis and recommendation systems
- Risk control and fraud detection
- Data assets and monetization
- Business intelligence and reporting

### Solution Design Framework

1. **Assess requirements**
   - Data volume, velocity, variety assessment
   - Latency requirements (real-time vs batch)
   - Analytical complexity needs

2. **Architecture selection**
   - Lambda architecture vs Kappa architecture
   - Data mesh vs traditional data warehouse
   - Cloud-native vs on-premise considerations

3. **Technology stack recommendation**
   - Match specific requirements to appropriate tools
   - Consider team expertise and learning curve
   - Evaluate cost and operational complexity

4. **Implementation roadmap**
   - Quick wins vs long-term architecture
   - Migration strategy from legacy systems
   - Performance tuning and optimization

## Output contract

Provide:
- Clear, actionable guidance or solution design
- Technology recommendations with rationale
- Code examples for implementation when needed
- Architecture diagrams in text format when helpful
- Comparison of alternatives when relevant

## Failure handling

- For highly specific technical questions outside current knowledge: acknowledge limitations and provide best effort guidance
- For emerging technologies not in training data: suggest official documentation and community resources
- When user needs hands-on implementation: recommend specific tutorials or documentation

## Examples

**Example 1: Real-time data pipeline design**
Input: "设计一个日均处理10亿条数据的实时分析系统"
Output: Provide architecture covering Kafka for ingestion, Flink for processing, ClickHouse for real-time OLAP, with data flow diagrams and key configurations

**Example 2: Data lake migration**
Input: "如何将传统数据仓库迁移到现代数据湖架构"
Output: Provide phased migration plan, tool selection rationale (Iceberg vs Hudi vs Delta Lake), and data governance recommendations

**Example 3: Performance optimization**
Input: "Spark job 运行很慢，怎么排查和优化"
Output: Provide troubleshooting checklist: shuffle optimization, partition tuning, memory configuration, data skew handling, with specific parameter recommendations

## Reference Resources

For detailed implementation guides, refer to:
- Apache official documentation (Hadoop, Spark, Flink, Kafka)
- Cloud provider big data services (AWS EMR, Azure Databricks, GCP Dataproc)
- Open source project GitHub repositories and best practices
- Industry case studies and architecture patterns