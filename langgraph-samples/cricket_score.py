from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from dotenv import load_dotenv
load_dotenv()

class BatsmanState(TypedDict):

    runs: int
    balls: int
    fours: int
    sixes: int
    sr: float
    bpb: float
    bnp: float
    sum: str

def calc_sr(state: BatsmanState):
    
    vsr = (state['runs']/state['balls']) * 100
    # state['sr'] = vsr
    # return state # Cannot return entire as other are doing same simultaneously
    return {'sr': vsr}

def calc_bpb(state: BatsmanState):
    
    vbpb = (state['balls']/(state['fours'] + state['sixes']))
    # state['bpb'] = vbpb
    # return state # Cannot return entire as other are doing same simultaneously
    return {'bpb': vbpb}

def calc_bnp(state: BatsmanState):
    
    vbnp = ((state['fours']*4 + state['sixes']*6)/state['runs']) * 100
    # state['bnp'] = vbnp
    # return state # Cannot return entire as other are doing same simultaneously
    return {'bnp': vbnp}

def calc_sum(state: BatsmanState):
    
    vsum = f"""
    Strike Rate - {state['sr']} \n
    Balls per boundary - {state['bpb']} \n
    Boundary percentage - {state['bnp']}
    """
    # state['sum'] = vsum
    # return state # Cannot return entire as other are doing same simultaneously
    return {'sum': vsum}

#create graph
graph = StateGraph(BatsmanState)

#create nodes
graph.add_node('Calculate_SR', calc_sr)
graph.add_node('Calculate_BPB', calc_bpb)
graph.add_node('Calculate_BNP', calc_bnp)
graph.add_node('Summary', calc_sum)

#create edges
graph.add_edge(START, 'Calculate_SR')
graph.add_edge(START, 'Calculate_BPB')
graph.add_edge(START, 'Calculate_BNP')
graph.add_edge('Calculate_SR', 'Summary')
graph.add_edge('Calculate_BPB', 'Summary')
graph.add_edge('Calculate_BNP', 'Summary')
graph.add_edge('Summary', END)

workflow = graph.compile()

initial_state = {
    'runs': 100,
    'balls': 50,
    'fours': 6,
    'sixes': 4
}

final_state = workflow.invoke(initial_state)
print(final_state)