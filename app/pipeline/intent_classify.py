import re
from sklearn.feature_extraction.text import TfidfVectorizer

TOOL_REPLACEMENTS = {
    r'\b(kafka|rabbitmq|nats|pulsar|sqs|sns|activemq|zeromq)\b': 'msg_queue',
    r'\b(postgres|postgresql|mysql|mongodb|redis|cassandra|dynamodb|elasticsearch|clickhouse|snowflake|redshift|bigquery)\b': 'database',
    r'\b(kubernetes|k8s|eks|gke|aks|nomad|ecs)\b': 'container_platform',
    r'\b(terraform|pulumi|cloudformation|ansible|helm|argocd|flux)\b': 'iac_tool',
    r'\b(jenkins|github.actions|gitlab.ci|circleci|tekton|drone)\b': 'cicd_tool',
    r'\b(aws|gcp|azure|s3|ec2|rds|gcs|blob)\b': 'cloud_provider',
    r'\b(fastapi|django|flask|spring|rails|express|nestjs|react|flutter|kotlin|rust|golang|python|java|typescript)\b': 'app_framework',
    r'\b(mlflow|kubeflow|airflow|spark|flink|tensorflow|pytorch|xgboost)\b': 'ml_tool',
    r'\b(datadog|prometheus|grafana|pagerduty|newrelic|splunk|kibana|jaeger)\b': 'observability_tool',
    }
    
INTENT_KEYWORDS = {
    'failing', 'crashed', 'error', 'timeout', 'unreachable', 'rejected',
    'blocked', 'stuck', 'down', 'unavailable', 'corrupted', 'missing',
    'expired', 'invalid', 'denied', 'exhausted', 'leak', 'duplicate',
    'slow', 'latency', 'lag', 'spike', 'overflow', 'oom', 'killed',
    'rotate', 'reset', 'restore', 'rollback', 'restart', 'grant', 'revoke',
    'update', 'migrate', 'deploy', 'provision', 'debug', 'investigate',
    'production', 'outage', 'blocking', 'degraded', 'data.loss', 'breach',
    }


def normalize_tools(text: str) -> str:
    text = text.lower()
    for pattern, replacement in TOOL_REPLACEMENTS.items():  
        text = re.sub(pattern, replacement, text)
    return text

def extract_intent_text(text: str) -> str:
    """
    Remove version numbers, commit hashes, IPs, ports, incident/PR numbers.
    """
    text = re.sub(r'\bv\d+[\.\d]+\b', '', text)
    text = re.sub(r'\b[a-f0-9]{7,40}\b', '', text)
    text = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '', text)
    text = re.sub(r':\d{2,5}\b', '', text)
    text = re.sub(r'\bpr\s*#?\d+\b', '', text)
    text = re.sub(r'\binc-?\d+\b', '', text)
    return text.strip()

def preprocess_single(description: str) -> str:

    return extract_intent_text(normalize_tools(description))

def build_intent_vectorizer(descriptions: list):
    """
    Fit the tfidf vectorizer on the training description. Call Once.
    """
    processed = [preprocess_single(d) for d in descriptions]
    temp_vec = TfidfVectorizer(
        stop_words='english',
        max_features=500,
        ngram_range=(1, 2),
        sublinear_tf=True
    )
    temp_vec.fit(processed)
    all_features = set(temp_vec.get_feature_names_out())

    tool_tokens = set(TOOL_REPLACEMENTS.values())
    noise_words = {'pr', 'inc', 'v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7', 'v8', 'v9', 'v10',
                   'v11', 'v12', 'v13', 'v14', 'v15', 'v16', 'v17', 'v18', 'v19', 'v20',
                   'commit', 'hash', 'ip', 'port', 'pr_number', 'inc_number'}
    final_vocab = sorted(all_features - tool_tokens - noise_words)

    intent_vectorizer = TfidfVectorizer(
        vocabulary=final_vocab,
        sublinear_tf=True,
        norm='l2'
    )
    intent_tfidf = intent_vectorizer.fit_transform(processed)
    return intent_vectorizer, intent_tfidf


