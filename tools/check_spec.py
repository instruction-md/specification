#!/usr/bin/env python3
"""Check schema/registry/vector consistency and structurally lint bundled samples.

This is not a full CommonMark parser or independent resolver implementation.
It makes no claim about renderer, live-provider or runtime conformance.
"""
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import yaml
from urllib.parse import unquote

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from build_registry import ROOT, documents, KINDS
from spec_support import scan_sample, walk, model_errors, text_profile, attrs, load_yaml, compose_fixture

failures=[];checks=0

def check(ok,message):
    global checks
    checks+=1
    if not ok:failures.append(message)
def read(path):return json.loads((ROOT/path).read_text())
def main():
    schemas=documents();reg=Registry()
    for name,data in schemas.items():
        if name.endswith('schema.json'):
            Draft202012Validator.check_schema(data)
            reg=reg.with_resource(data['$id'],Resource.from_contents(data))
        check(read(name)==data,'Generated artifact drift: '+name)
    def validator(name):return Draft202012Validator(schemas[name],registry=reg,format_checker=FormatChecker())
    authored=validator('instruction.schema.json')
    for case in read('conformance/model/cases.json'):
        valid=authored.is_valid(case['document'])
        check(valid==case['valid'],'Model vector: '+case['name'])
    for case in read('conformance/source/cases.json'):
        try:
            tree=scan_sample(case['source']);valid=True
        except (ValueError,yaml.YAMLError) as exc:
            valid=False;tree=None
        check(valid==case['valid'],'Source structural check: '+case['name'])
        if not tree:continue
        directives=[n for n,_ in walk(tree['body']) if n['type']=='directive']
        if 'directives' in case:check(len(directives)==case['directives'],'Directive count: '+case['name'])
        if 'title' in case:check(directives[0]['attrs']['title']==case['title'],'Quoted attribute: '+case['name'])
        if 'not' in case:check(directives[0]['attrs'].get('not')==case['not'],'Negation: '+case['name'])
        if 'back' in case:check(tree['metadata']['back']==case['back'],'Backmatter: '+case['name'])
        if 'notes' in case:check(tree['metadata']['front']['notes']==case['notes'],'YAML 1.2 strings: '+case['name'])
        if 'markdown' in case:check(tree['body'][0]['source']==case['markdown'],'Comment tail: '+case['name'])
    for path in sorted((ROOT/'conformance/text').glob('*.json')):
        value=json.loads(path.read_text());check(authored.is_valid(value),'Text vector schema: '+path.stem)
        check(text_profile(value)==path.with_suffix('.txt').read_text(),'Exact text vector: '+path.stem)
    for case in read('conformance/resolution/cases.json'):
        try:
            effective,origins=compose_fixture(case['document'],case['documents'])
            check('error' not in case,'Expected composition failure: '+case['name'])
            summary=[]
            for node in effective['body']:
                if node.get('attrs',{}).get('id'):
                    summary.append({'instance':node['instance'],'id':node['attrs']['id'],'kind':node['kind'],
                                    'text':'|'.join(n['source'] for n,_ in walk(node.get('children',[])) if n['type']=='markdown')})
            if 'expected_value' in case:
                check(effective['body'][0]['value']['data']==case['expected_value'],'Structured composition result: '+case['name'])
            else:
                check(summary==case.get('expected'),'Composition result: '+case['name'])
            check([x['operation'] for x in origins if x.get('operation') in ('replace','extend','remove')]==case.get('changes'),'Composition provenance: '+case['name'])
        except ValueError as exc:check(str(exc)==case.get('error'),'Composition diagnostic: '+case['name']+' '+str(exc))
    # Deliberate cross-node constraints outside JSON Schema.
    duplicate={'format':'instruction/1','body':[{'type':'directive','kind':'person','form':'leaf','attrs':{'id':'a'}},{'type':'directive','kind':'role','form':'leaf','attrs':{'id':'a'}}]}
    check('duplicate-id' in model_errors(duplicate),'Cross-kind duplicate identity')
    parent={'format':'instruction/1','body':[{'type':'directive','kind':'tab','form':'container','attrs':{},'children':[]}]}
    check('invalid-nesting' in model_errors(parent),'Out-of-place tab')
    for file,schema in [('conformance/resolved.json','schemas/resolved.schema.json'),('samples/morning-assistant/resolved.json','schemas/resolved.schema.json'),('conformance/test-request.json','schemas/testing.schema.json'),('conformance/test-result.json','schemas/testing.schema.json'),('samples/morning-assistant/bundle-manifest.json','schemas/bundle.schema.json')]:
        errors=list(validator(schema).iter_errors(read(file)))
        check(not errors,'Exchange schema '+file+': '+str([e.message for e in errors]))
    for p in (ROOT/'samples').rglob('*.extension.json'):
        check(validator('schemas/extension.schema.json').is_valid(json.loads(p.read_text())),'Extension manifest: '+str(p))
    # Negative exchange probes catch weak contract regressions.
    for name,file,mutate in [
      ('resolved status','conformance/resolved.json',lambda d:d.update(status='silently-truncated')),
      ('test pass enum','conformance/test-result.json',lambda d:d.update(status='mostly-passed')),
      ('bundle traversal','samples/morning-assistant/bundle-manifest.json',lambda d:d.update(main='../outside.md'))]:
        d=copy.deepcopy(read(file));mutate(d)
        schema='schemas/resolved.schema.json' if 'resolved' in name else 'schemas/testing.schema.json' if name.startswith('test') else 'schemas/bundle.schema.json'
        check(not validator(schema).is_valid(d),'Negative exchange: '+name)
    catalog={m['id']:m for m in (json.loads(p.read_text()) for p in (ROOT/'samples').rglob('*.extension.json'))}
    seen=set()
    for p in sorted((ROOT/'samples').rglob('*.md')):
        if p.name in ('README.md','SKILL.md'):continue
        try:
            tree=scan_sample(p.read_text(),p.as_uri(),catalog=catalog)
            errors=list(authored.iter_errors(tree))
            check(not errors,'Sample schema '+str(p.relative_to(ROOT))+': '+str([(list(e.absolute_path),e.message) for e in errors]))
            check(not model_errors(tree),'Sample cross-node constraints: '+str(p.relative_to(ROOT)))
            for n,_ in walk(tree['body']):
                if n['type']=='directive':
                    seen.add(n['kind'])
                    if ':' in n['kind']:
                        alias,kind=n['kind'].split(':',1);binding=tree['metadata']['front']['extensions'][alias];definition=catalog[binding['id']]['provides']['blocks'][kind]
                        props={**schemas['registry.json']['common_attributes'],**definition['attributes']}
                        check(Draft202012Validator({'type':'object','properties':props,'additionalProperties':False}).is_valid(n['attrs']),'Extension attribute types: '+n['kind'])
                for key in ('src','preview','transcript','stylesheet'):
                    value=n.get('attrs',{}).get(key)
                    if value and not re.match(r'^[a-z][a-z0-9+.-]*:',value) and not value.startswith('#'):
                        target=(p.parent/unquote(value.split('#',1)[0])).resolve()
                        check(target.is_file(),'Local resource: '+str(p.relative_to(ROOT))+' '+value)
        except Exception as exc:check(False,'Sample scan '+str(p.relative_to(ROOT))+': '+str(exc))
    bundle=read('samples/morning-assistant/bundle-manifest.json');base=ROOT/'samples/morning-assistant'
    paths=[e['path'] for e in bundle['entries']]
    check(len(paths)==len(set(paths)),'Bundle duplicate path')
    check(bundle['main'] in paths,'Bundle includes main')
    for entry in bundle['entries']:
        p=base/entry['path']
        check(p.is_file(),'Bundle entry exists: '+entry['path'])
        if p.is_file():check('sha256:'+hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256'],'Bundle digest: '+entry['path'])
    # The AgentD example has traceable native exports, without starting a runtime.
    from build_agentd_sample import artifacts, graph_errors
    generated,cfg,flows=artifacts();agentd_base=ROOT/'samples/agentd-assistant'
    for name,data in generated.items():
        check((agentd_base/name).read_bytes()==data,'AgentD artifact drift: '+name)
    compiled=json.loads(generated['instruction.json'])
    check(validator('schemas/bundle.schema.json').is_valid(compiled),'Compiled export manifest schema')
    indexed={entry['path']:entry for entry in compiled['entries']}
    check(len({e['id'] for e in compiled['exports']})==len(compiled['exports']),'Unique native export IDs')
    for export in compiled['exports']:
        check(export['path'] in indexed,'Export entry exists: '+export['id'])
        check(indexed[export['path']]['sha256']==export['sha256'],'Export digest: '+export['id'])
        for source in export['sources']:
            check(source['sha256']=='sha256:'+hashlib.sha256((agentd_base/'instruction.md').read_bytes()).hexdigest(),'Export source provenance: '+export['id'])
    check(not graph_errors(flows[0]),'AgentD example graph references and dependencies')
    broken=copy.deepcopy(flows[0]);broken['steps']['draft']['depends_on']=['missing']
    check('missing-dependency' in graph_errors(broken),'Missing workflow dependency rejected')
    broken=copy.deepcopy(flows[0]);broken['steps']['route']['cases']['accept']='missing'
    check('missing-route' in graph_errors(broken),'Missing workflow route rejected')
    broken=copy.deepcopy(flows[0]);broken['steps']['start']['depends_on']=['draft']
    check('dependency-cycle' in graph_errors(broken),'Workflow dependency cycle rejected')
    # Native Instruction Workflows: schema + independent expected error vectors.
    from workflow_support import workflow_errors
    workflow_validator=validator('schemas/workflow.schema.json')
    for case in read('conformance/workflows/cases.json'):
        shape=workflow_validator.is_valid(case['workflow'])
        errors=workflow_errors(case['workflow']) if shape else ['schema']
        check((not errors)==case['valid'],'Native workflow: '+case['name'])
        if not case['valid']:check(case['error'] in errors,'Native workflow diagnostic: '+case['name'])
    for p in (ROOT/'samples/workflows').glob('*.yaml'):
        flow=load_yaml(p.read_text())
        check(workflow_validator.is_valid(flow),'Native workflow schema: '+p.name)
        check(not workflow_errors(flow),'Native workflow graph: '+p.name)
    # Documentation links outside code spans/fences. External links are not fetched.
    for p in [ROOT/'README.md',ROOT/'guide/README.md',ROOT/'guide/cheatsheet.md',ROOT/'guide/workflows.md',
              ROOT/'reference/markdown.md',ROOT/'reference/workflows.md',ROOT/'reference/workflow-nodes.md',ROOT/'schemas/README.md']:
        in_code=False
        for line in p.read_text().splitlines():
            if line.startswith('```'):in_code=not in_code;continue
            if in_code:continue
            line=re.sub(r'`+[^`]*`+', '', line)
            for target in re.findall(r'\]\(([^)]+)\)',line):
                if ':' in target or target.startswith('#'):continue
                path=target.split('#',1)[0]
                if path:check((p.parent/path).exists(),'Document link '+str(p.relative_to(ROOT))+': '+target)
    print(f'{checks} checks; {len(KINDS)} core block kinds; {len(seen)} kinds exercised in the authored samples.')
    if failures:
        print('\n'.join('FAIL: '+x for x in failures));raise SystemExit(1)
    print('PASS: generated schemas, model/source/text vectors, sample structure, local resources, bundle digests and documentation links.')
    print('Not verified: full Markdown parsing, independent resolution, live integrations, rich rendering, JCS implementation or runtime execution.')
if __name__=='__main__':main()
