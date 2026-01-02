from aws_cdk import App
from stock_analytics_pipeline.infastructure.infastructure_stack import InfrastructureStack #Can be shortened using __init__.py

app = App()
InfrastructureStack(app, "StockAnalyticsPipelineStack")
app.synth()