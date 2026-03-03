from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated
from pydantic import BaseModel, Field
import operator # for reducer function
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(model= 'gpt-4o-mini')

class EvaluationSchema(BaseModel):
    feedback: str = Field(description= 'Detailed feedback for the essay')
    score: int = Field(description='Score out of 10', ge= 0, le= 10)

structured_model = model.with_structured_output(EvaluationSchema)

essay = """
India's AI (artificial intelligence) ecosystem has grown quickly over the last decade, moving from primarily academic research to real-world adoption across government and industry. A major driver has been the expansion of digital public infrastructure and large-scale digitization, which has created more data and clearer use cases for automation, prediction, and citizen-facing services. At the same time, India's large pool of engineering talent and a strong IT services sector have helped accelerate experimentation and deployment, especially in areas like customer support, document processing, and software development.
In the private sector, banks and fintech firms increasingly use AI for fraud detection, credit risk assessment, and personalized customer experiences. Healthcare providers and startups are applying machine learning to improve diagnostics, triage, and operational planning, while agriculture initiatives use AI-enabled analytics to support yield forecasting and advisory services. Indian enterprises are also investing in AI to optimize supply chains, energy usage, and manufacturing quality. More recently, generative AI tools have broadened interest beyond data science teams, making AI more accessible to business users and speeding up prototyping.
However, the growth of AI in India also faces constraints. Data quality, interoperability, and privacy safeguards remain uneven across sectors. Many organizations struggle to move from pilots to scaled deployment due to limited governance, unclear ROI (return on investment), and a shortage of specialized skills in areas such as MLOps (machine learning operations), model risk management, and AI security. Bias, transparency, and accountability are additional concerns, especially when AI is used in high-impact decisions.
Overall, AI in India is shifting from “emerging technology” to “core capability.” Continued progress will depend on practical regulation, responsible data practices, workforce development, and sustained investment in compute and research. If these pieces align, AI could significantly improve productivity and public service delivery while enabling new products and business models across the economy.
"""

essay2 = """
AI is growing a lot in India these days and you can see it almost everywhere. Earlier mostly only big companies was talking about AI, but now even small startups and students are using it. Many peoples use AI apps for making photos, writing text, and doing study help, so it is becoming normal thing.
In offices, banks and call centers are using AI to answer customers faster, and to find fraud also. In hospitals some doctors are trying AI for checking reports and scans, but it is not perfect so they still need human doctor. In farming side, some projects use AI for weather and crop advice, but many farmers still don't have good internet so it becomes hard.
Government is also pushing digital stuff, like online services and data systems, so AI can be used for making services faster. But there is also problems. Data privacy is not always clear, and many times the data is messy so AI gives wrong result. Also jobs fear is there, because people think AI will take jobs, but it can also create new jobs if we learn it.
Overall AI in India is growing fast, but it need better rules, better training, and more responsible use.
"""

# prompt = f'Evaluate the language quality of the following essay and provide a feedback and assign a score out of 10 \n {essay}'
# structured_model.invoke(prompt)

class EssayState(TypedDict):
    essay: str
    language_fb: str
    analysis_fb: str
    clarity_fb: str
    overall_fb: str
    individual_scores: Annotated[list[int], operator.add] #reducer func to merge/append values into same list instead of replace
    avg_score: float

def evaluate_language(state: EssayState):
    prompt = f'Evaluate the language quality of the following essay and provide a feedback and assign a score out of 10 \n {state['essay']}'
    output = structured_model.invoke(prompt)
    return {'language_fb': output.feedback, 'individual_scores': [output.score]}

def evaluate_analysis(state: EssayState):
    prompt = f'Evaluate the depth of analysis of the following essay and provide a feedback and assign a score out of 10 \n {state['essay']}'
    output = structured_model.invoke(prompt)
    return {'analysis_fb': output.feedback, 'individual_scores': [output.score]}

def evaluate_thought(state: EssayState):
    prompt = f'Evaluate the clarity of thought of the following essay and provide a feedback and assign a score out of 10 \n {state['essay']}'
    output = structured_model.invoke(prompt)
    return {'clarity_fb': output.feedback, 'individual_scores': [output.score]}

def overall_evaluation(state: EssayState):
    prompt = f'Based on the following feedbacks create a summarized feedback \n language feedback - {state['language_fb']} \n depth of analysis feedback - {state['analysis_fb']} \n clarity of thought feedback - {state['clarity_fb']}'
    overall_feedback = model.invoke(prompt).content
    #average
    avg_score = sum(state['individual_scores'])/len(state['individual_scores'])
    return {'overall_fb': overall_feedback, 'avg_score': avg_score}

graph = StateGraph(EssayState)

graph.add_node('evaluate_language', evaluate_language)
graph.add_node('evaluate_analysis', evaluate_analysis)
graph.add_node('evaluate_thought', evaluate_thought)
graph.add_node('overall_evaluation', overall_evaluation)

graph.add_edge(START, 'evaluate_language')
graph.add_edge(START, 'evaluate_analysis')
graph.add_edge(START, 'evaluate_thought')
graph.add_edge('evaluate_language', 'overall_evaluation')
graph.add_edge('evaluate_analysis', 'overall_evaluation')
graph.add_edge('evaluate_thought', 'overall_evaluation')
graph.add_edge('overall_evaluation', END)

workflow = graph.compile()

initial_state = {
    'essay': essay
    # 'essay': essay2
}

final_state = workflow.invoke(initial_state)
print(final_state)