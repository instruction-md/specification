#!/usr/bin/env python3
"""Build/check the authored AgentD example; not a general Instruction compiler."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import yaml
from spec_support import scan_sample, walk, text_profile
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'samples/agentd-assistant'
URI='https://example.org/samples/agentd-assistant/'
def digest(data):return 'sha256:'+hashlib.sha256(data).hexdigest()
def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
def graph_errors(flow):
    steps=flow.get('steps',{});errors=[]
    for name,step in steps.items():
        for dep in step.get('depends_on',[]):
            if dep not in steps:errors.append('missing-dependency')
        if step.get('kind')=='switch':
            for target in step.get('cases',{}).values():
                if target not in steps:errors.append('missing-route')
    visiting=set();done=set()
    def visit(name):
        if name in visiting:errors.append('dependency-cycle');return
        if name in done:return
        visiting.add(name)
        for dep in steps[name].get('depends_on',[]):
            if dep in steps:visit(dep)
        visiting.remove(name);done.add(name)
    for name in steps:visit(name)
    return errors

def artifacts():
    source=(BASE/'instruction.md').read_bytes();tree=scan_sample(source.decode(),URI+'instruction.md')
    nodes={n['attrs']['id']:n for n,_ in walk(tree['body']) if n.get('attrs',{}).get('id')}
    bindings=tree['metadata']['front']['exports']['morning']['bindings']
    def get(reference,kind):
        node=nodes[reference.removeprefix('#')]
        if node['kind']!=kind:raise ValueError('Binding kind mismatch')
        return node
    cfg=copy.deepcopy(get(bindings['config'],'config')['value']['data'])
    if 'mcp' in cfg or 'workflows' in cfg:raise ValueError('export-conflict')
    if cfg['agent']['instruction']['file']!='./guidance.md' or cfg['skills']['dir']!='./skills':raise ValueError('Export paths differ from the example profile')
    outputs={};records=[]
    def add(path,data,id_,kind,select=None,dialect=None):
        outputs[path]=data
        rec={'id':id_,'kind':kind,'path':path,'sha256':digest(data),'adapter':'agentd','profile':'agentd/1',
             'sources':[{'uri':URI+'instruction.md','sha256':digest(source),**({'select':{'id':select}} if select else {})}]}
        if dialect:rec['dialect']=dialect
        records.append(rec)
    guidance=get(bindings['instruction'],'instruction')
    add('guidance.md',text_profile({'body':guidance['children']}).encode(),'guidance','agent-instructions',guidance['attrs']['id'])
    servers=[]
    for ref in bindings['servers']:
        attrs=get(ref,'mcp')['attrs'];server={'name':attrs['id'],'ns':attrs['id'],'endpoint':attrs['src']}
        if attrs.get('allow',attrs.get('tools')):server['allow']=attrs.get('allow',attrs.get('tools'))
        if attrs.get('deny'):server['exclude']=attrs['deny']
        servers.append(server)
    cfg['mcp']={'servers':servers}
    for ref in bindings['skills']:
        skill=get(ref,'skill');a=skill['attrs']
        header=yaml.safe_dump({'name':a['id'],'description':a['description']},sort_keys=False)
        data=('---\n'+header+'---\n\n'+text_profile({'body':skill['children']})).encode()
        add('skills/'+a['id']+'/SKILL.md',data,a['id'],'skill',a['id'])
    workflows=[]
    for ref in bindings['workflows']:
        node=get(ref,'workflow');flow=copy.deepcopy(node['value']['data'])
        if graph_errors(flow):raise ValueError('invalid-workflow')
        workflows.append(flow)
        add('workflows/'+flow['name']+'.json',encode(flow),node['attrs']['id'],'workflow',node['attrs']['id'],'agentd/workflow')
    if len({x['name'] for x in workflows})!=len(workflows):raise ValueError('export-conflict')
    cfg['workflows']=workflows
    add('agentd.json',encode(cfg),'runtime','config',dialect='agentd/config')
    entries=[];mapping={}
    for name,data in {'instruction.md':source,**outputs}.items():
        uri=URI+name;mapping[uri]=name
        entries.append({'path':name,'uri':uri,'media_type':'application/json' if name.endswith('.json') else 'text/markdown','sha256':digest(data)})
    outputs['instruction.json']=encode({'format':'instruction-bundle/1','main':'instruction.md','complete':False,'entries':entries,'mapping':mapping,'exports':records})
    return outputs,cfg,workflows

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');parser.add_argument('--config-schema');parser.add_argument('--workflow-schema');args=parser.parse_args()
    outputs,cfg,flows=artifacts()
    for name,data in outputs.items():
        path=BASE/name
        if args.check:
            if not path.is_file() or path.read_bytes()!=data:raise ValueError('Generated artifact drift: '+name)
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    if args.config_schema or args.workflow_schema:
        from jsonschema import Draft202012Validator
        for file,value,expected in [(args.config_schema,cfg,'e9d632c2298d3e8ff80ec4f33419b6449ecd79e69853c75b37a071be7e562f5d'),(args.workflow_schema,flows,'40f1d4a06967af70705d1b6aa508ebcc7defc7693ad3e8d8570eb02637ac5f23')]:
            if not file:continue
            raw=Path(file).read_bytes()
            if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('Upstream schema pin mismatch')
            validator=Draft202012Validator(json.loads(raw))
            for item in value if isinstance(value,list) else [value]:validator.validate(item)
    print(('Checked' if args.check else 'Generated')+' original AgentD example, native artifacts and export manifest. No runtime was activated.')
if __name__=='__main__':main()
