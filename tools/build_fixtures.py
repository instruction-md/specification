#!/usr/bin/env python3
"""Build fixture data for the spec's model/schema checks, not reader conformance."""
import copy
import hashlib
import json
from pathlib import Path
from build_registry import ROOT,KINDS,COMMON
from spec_support import compose_fixture, scan_sample, text_profile, walk, stamp

def write(path,value):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def md(text):return {'type':'markdown','source':text}
def directive(kind,attrs=None,text='Shared content.',form='container'):
    d=KINDS[kind];a=dict(attrs or {})
    for key in d['required']:
        a.setdefault(key, {'id':'sample','src':'./resource.md','as':'shared','name':'sample','target':'#base/block','server':'#server','component':'example-card'}.get(key,'sample'))
    result={'type':'directive','kind':kind,'form':form,'attrs':a}
    if form!='leaf':
        if d['body']=='yaml':result['value']={'format':'yaml','source':'{}\n','data':{}}
        elif d['body']!='none':result['children']=[md(text)]
    return result

def main():
    cases=[]
    for kind,d in sorted(KINDS.items()):
        form='container' if 'container' in d['forms'] else d['forms'][0]
        node=directive(kind,form=form)
        if d.get('parent'):
            parent=directive(d['parent']);parent['children']=[node];body=[parent]
        else:body=[node]
        doc={'format':'instruction/1','body':body}
        cases.append({'name':kind+'-valid','valid':True,'document':doc})
        bad=copy.deepcopy(doc)
        target=bad['body'][0]['children'][0] if d.get('parent') else bad['body'][0]
        target['attrs']['unregistered-core-attribute']='not allowed'
        cases.append({'name':kind+'-unknown-attribute','valid':False,'document':bad})
    edge=[
      ('id-with-spaces',directive('person',{'id':'not a valid id'},form='leaf')),
      ('enum-without-values',directive('param',{'name':'tier','type':'enum'},form='leaf')),
      ('column-span',directive('column',{'span':13})),
      ('must-leaf',directive('must',form='leaf')),
      ('output-response-format',directive('output',{'response-format':'json'})),
    ]
    for name,node in edge:cases.append({'name':name,'valid':name=='output-response-format','document':{'format':'instruction/1','body':[node]}})
    cases.append({'name':'agent-by-endpoint','valid':True,'document':{'format':'instruction/1','body':[directive('agent',{'protocol':'a2a','endpoint':'https://agents.example.org/a2a/v1','binding':'JSONRPC','tenant':'bookings','skills':['search','reserve']},form='leaf')]}})
    cases.append({'name':'front-and-back-metadata','valid':True,'document':{'format':'instruction/1','metadata':{'front':{'title':'Shared guidance'},'back':{'authors':['Alex'],'custom':{'reviewed':True}}},'body':[]}})
    cases.append({'name':'unknown-metadata-region','valid':False,'document':{'format':'instruction/1','metadata':{'trailing':{}},'body':[]}})
    write('conformance/model/cases.json',cases)
    sources=[
      {'name':'quoted-escape','source':':::context{title="She said \\"no\\""}\nShared.\n:::\n','valid':True,'title':'She said "no"'},
      {'name':'indented-fence-is-code','source':'   ```markdown\n:::unknown\n   ```\n','valid':True,'directives':0},
      {'name':'indented-directive-is-prose','source':'    :::unknown\n','valid':True,'directives':0},
      {'name':'shorter-inner-fences','source':'::::columns\n:::card{title="A"}\nShared.\n:::\n::::\n','valid':True,'directives':2},
      {'name':'equal-inner-fences','source':':::columns\n:::card\n:::\n:::\n','valid':False},
      {'name':'code-fences-as-tabs','source':':::tabs\n```bash {title="npm"}\nnpm install instruction.md\n```\n```bash {title="pnpm"}\npnpm add instruction.md\n```\n:::\n','valid':True,'directives':1},
      {'name':'plain-backmatter-to-eof','source':'Shared.\n\n---\nowners: [Alex]\n','valid':True,'back':{'owners':['Alex']},'markdown':'Shared.\n\n'},
      {'name':'backmatter-after-front-matter','source':'---\ntitle: Shared guidance\n---\nShared.\n\n---\nauthors: [Alex]\n','valid':True,'back':{'authors':['Alex']},'markdown':'Shared.\n\n'},
      {'name':'backmatter-with-yaml-comments','source':'Shared.\n\n---\n\n# Review record\nhistory: [{summary: Clarified the goal}]\ncustom: preserved\n','valid':True,'back':{'history':[{'summary':'Clarified the goal'}],'custom':'preserved'}},
      {'name':'thematic-break-stays-body','source':'Shared.\n\n---\nAnother paragraph.\n','valid':True,'back':{},'markdown':'Shared.\n\n---\nAnother paragraph.\n'},
      {'name':'unknown-first-key-stays-body','source':'Shared.\n\n---\ncustom: body text\nauthors: also body text\n','valid':True,'back':{},'markdown':'Shared.\n\n---\ncustom: body text\nauthors: also body text\n'},
      {'name':'setext-underline-stays-body','source':'Shared\n---\nauthors: ordinary prose\n','valid':True,'back':{},'markdown':'Shared\n---\nauthors: ordinary prose\n'},
      {'name':'alternative-thematic-break','source':'Shared.\n\n***\nauthors: ordinary prose\n','valid':True,'back':{},'markdown':'Shared.\n\n***\nauthors: ordinary prose\n'},
      {'name':'escaped-backmatter-marker','source':'Shared.\n\n\\---\nauthors: ordinary prose\n','valid':True,'back':{},'markdown':'Shared.\n\n\\---\nauthors: ordinary prose\n'},
      {'name':'backmatter-looking-code','source':'```yaml\n\n---\nauthors: [Alex]\n```\n','valid':True,'back':{},'markdown':'```yaml\n\n---\nauthors: [Alex]\n```\n'},
      {'name':'backmatter-looking-container','source':':::context\nShared.\n\n---\nauthors: [Alex]\n:::\n','valid':True,'back':{},'directives':1},
      {'name':'backmatter-looking-blockquote','source':'> Shared.\n>\n> ---\n> authors: [Alex]\n','valid':True,'back':{},'markdown':'> Shared.\n>\n> ---\n> authors: [Alex]\n'},
      {'name':'backmatter-looking-html','source':'<pre>\nShared.\n\n---\nauthors: [Alex]\n</pre>\n','valid':True,'back':{},'markdown':'<pre>\nShared.\n\n---\nauthors: [Alex]\n</pre>\n'},
      {'name':'backmatter-duplicate-key','source':'Shared.\n\n---\nauthors: [Alex]\nauthors: [Jordan]\n','valid':False},
      {'name':'backmatter-invalid-yaml','source':'Shared.\n\n---\nauthors: [Alex\n','valid':False},
      {'name':'backmatter-no-closing-fence','source':'Shared.\n\n---\nauthors: [Alex]\n---\n','valid':False},
      {'name':'comment-preserves-tail','source':'a<!-- reviewer -->b\n','valid':True,'markdown':'ab\n'},
      {'name':'should-not-keeps-negation','source':'SHOULD NOT: disclose private details.\n','valid':True,'not':True},
      {'name':'example-does-not-extract-rules','source':':::example\nMUST[not-a-rule]: quoted.\n:::\n','valid':True,'directives':1},
      {'name':'unclosed-directive','source':':::policy\nShared.\n','valid':False},
      {'name':'duplicate-yaml-key','source':'---\ntitle: a\ntitle: b\n---\nShared.\n','valid':False},
      {'name':'yaml-date-and-on-stay-strings','source':'---\nnotes: {on: 2026-10-26}\n---\nShared.\n','valid':True,'notes':{'on':'2026-10-26'}},
      {'name':'yaml-anchors-forbidden','source':'---\nnotes: &a value\n---\n','valid':False},
      {'name':'duplicate-attribute','source':'::person{id=a id=b}\n','valid':False},
      {'name':'opaque-extension','source':':::charts:metric{value=1}\n:::unknown\n:::\n','valid':True,'directives':1},
    ]
    write('conformance/source/cases.json',sources)
    text_cases=[
      ('rule',{'format':'instruction/1','body':[directive('should',{'not':True},'disclose private details.')]},'SHOULD NOT: disclose private details.\n'),
      ('reason',{'format':'instruction/1','body':[directive('must',{'if':'an event is tentative','because':'Status matters.'},'retain its status.')]},'MUST (if an event is tentative): retain its status.\nBECAUSE: Status matters.\n'),
      ('literal-blank-lines',{'format':'instruction/1','body':[directive('script',{'id':'s'},'```python\na = 1\n\n\nprint(a)\n```\n')]},'### script: s\n\n```python\na = 1\n\n\nprint(a)\n```\n'),
      ('labelled-example',{'format':'instruction/1','body':[directive('example',{'title':'Quoted'},'MUST: this is an example.')]},'### Example: Quoted\n\n```markdown\nMUST: this is an example.\n```\n'),
      ('all-tabs',{'format':'instruction/1','body':[{'type':'directive','kind':'tabs','form':'container','attrs':{},'children':[directive('tab',{'title':'A'},'First.'),directive('tab',{'title':'B'},'Second.')]}]},'### tabs: tabs\n\n### tab: A\n\nFirst.\n\n### tab: B\n\nSecond.\n'),
    ]
    for name,doc,expected in text_cases:
        write('conformance/text/'+name+'.json',doc);(ROOT/('conformance/text/'+name+'.txt')).write_text(expected)
    sample={'format':'instruction-resolved/1','status':'complete',
      'document':{'uri':'https://example.org/simple.md','sha256':'sha256:'+'0'*64},
      'body':[stamp(directive('policy',{'id':'privacy','title':'Privacy'},'Keep private details private.'),'root')],
      'extensions':[],'objects':[],'resources':[],'dependencies':[],'provenance':[],'diagnostics':[]}
    write('conformance/resolved.json',sample)
    write('conformance/test-request.json',{'format':'instruction-test-request/1','id':'sample-test','document_digest':'sha256:'+'0'*64,'target':'#formatter','adapter':'example/python','inputs':{'status':'tentative'}})
    write('conformance/test-result.json',{'format':'instruction-test-result/1','request':'sample-test','document_digest':'sha256:'+'0'*64,'status':'skipped','environment':{'reason':'No external adapter configured'},'started':'2026-10-26T12:00:00Z','finished':'2026-10-26T12:00:00Z','assertions':[],'artifacts':[]})
    base={'format':'instruction/1','uri':'base.md','body':[
      directive('instruction',{'id':'length'},'Original length.'),
      directive('policy',{'id':'priorities'},'Commitments first.'),
      directive('instruction',{'id':'obsolete'},'Mail routine.')]}
    def child(body,extends=True):
        return {'format':'instruction/1','uri':'child.md','metadata':{'front':{'extends':[{'uri':'base.md','as':'personal'}]} if extends else {}},'body':body}
    resolution=[
      {'name':'explicit-body-modifications','documents':{'base.md':base},
       'document':child([directive('replace',{'target':'#personal/length'},'Shorter length.'),directive('extend',{'target':'#personal/priorities'},'Focus time.'),directive('remove',{'target':'#personal/obsolete'},form='leaf')]),
       'expected':[{'instance':'root/personal','id':'length','kind':'instruction','text':'Shorter length.'},{'instance':'root/personal','id':'priorities','kind':'policy','text':'Commitments first.|Focus time.'}],
       'changes':['replace','extend','remove']},
      {'name':'missing-patch-target','documents':{'base.md':base},'document':child([directive('remove',{'target':'#personal/missing'},form='leaf')]),'error':'patch-target'},
      {'name':'removed-target-cannot-be-patched','documents':{'base.md':base},'document':child([directive('remove',{'target':'#personal/length'},form='leaf'),directive('extend',{'target':'#personal/length'},'Later.')]),'error':'patch-target'},
      {'name':'separate-include-instances','documents':{'base.md':base},'document':child([directive('include',{'src':'base.md#id=length','as':'one'},form='leaf'),directive('include',{'src':'base.md#id=length','as':'two'},form='leaf')],False),
       'expected':[{'instance':'root/one','id':'length','kind':'instruction','text':'Original length.'},{'instance':'root/two','id':'length','kind':'instruction','text':'Original length.'}],'changes':[]},
      {'name':'inheritance-cycle','documents':{'base.md':{'format':'instruction/1','uri':'base.md','metadata':{'front':{'extends':[{'uri':'child.md','as':'again'}]}},'body':[]}},'document':child([]),'error':'composition-cycle'},
    ]
    resolution[-1]['documents']['child.md']=resolution[-1]['document']
    structured_base={'format':'instruction/1','uri':'base.md','body':[directive('data',{'id':'settings'})]}
    structured_patch={'type':'directive','kind':'replace','form':'container','attrs':{'target':'#personal/settings','format':'yaml'},'value':{'format':'yaml','source':'limit: 1\n','data':{'limit':1}}}
    resolution.append({'name':'structured-replacement','documents':{'base.md':structured_base},'document':child([structured_patch]),
      'expected_value':{'limit':1},'changes':['replace']})
    write('conformance/resolution/cases.json',resolution)
    root=ROOT/'samples/morning-assistant'
    manifest=json.loads((root/'extensions/charts.extension.json').read_text())
    main_tree=scan_sample((root/'instruction.md').read_text(),'https://example.org/samples/morning-assistant/instruction.md',catalog={manifest['id']:manifest})
    source_docs={('./'+name):scan_sample((root/name).read_text(),'https://example.org/samples/morning-assistant/'+name) for name in ['base.md','team.md']}
    effective,origins=compose_fixture(main_tree,source_docs)
    # The sample's only parameter occurrence is prose, outside code/literal content.
    for node,_ in walk(effective['body']):
        if node['type']=='markdown' and 'in ${timezone}.' in node['source']:
            node['source']=node['source'].replace('in ${timezone}.','in America/Toronto.')
    snapshot={'format':'instruction-resolved/1','status':'partial',
      'document':{'uri':main_tree['uri'],'sha256':'sha256:'+hashlib.sha256((root/'instruction.md').read_bytes()).hexdigest()},
      'body':effective['body'],'extensions':[{'instance':'root','alias':'charts','id':manifest['id'],'version':manifest['version'],'sha256':'sha256:'+hashlib.sha256((root/'extensions/charts.extension.json').read_bytes()).hexdigest()}],'objects':[],'resources':[],'dependencies':[], 'provenance':origins,'diagnostics':[]}
    for node,_ in walk(effective['body']):
        if node.get('kind') in ('person','mcp','agent'):
            a=node['attrs'];snapshot['objects'].append({'key':'root/'+a['id'],'kind':node['kind'],'label':a['title'],'target':a['src'],'status':'unresolved'})
            snapshot['diagnostics'].append({'code':'reference-optional','severity':'warning','message':'Fictional provider not contacted by the offline sample builder.','target':a['src']})
    for name in ['base.md','team.md','extensions/charts.extension.json','skills/prioritize/SKILL.md','assets/brief.svg','assets/brief.canvas','assets/format_events.py','assets/brief.css']:
        uri='https://example.org/samples/morning-assistant/'+name
        snapshot['dependencies'].append({'uri':uri,'resolved_uri':uri,'sha256':'sha256:'+hashlib.sha256((root/name).read_bytes()).hexdigest(),'mode':'live','instance':'root','extensions':{'charts':'1.0.0'} if name.endswith('extension.json') else {}})
    write('samples/morning-assistant/resolved.json',snapshot)
    (root/'resolved.txt').write_text(text_profile(snapshot))
    entries=[];mapping={}
    for p in sorted(root.rglob('*')):
        if not p.is_file() or p.name=='bundle-manifest.json':continue
        path=p.relative_to(root).as_posix();uri='https://example.org/samples/morning-assistant/'+path
        media={'md':'text/markdown','json':'application/json','svg':'image/svg+xml','canvas':'application/json','py':'text/x-python','css':'text/css'}.get(p.suffix[1:],'application/octet-stream')
        entries.append({'path':path,'uri':uri,'media_type':media,'sha256':'sha256:'+hashlib.sha256(p.read_bytes()).hexdigest()});mapping[uri]=path
    write('samples/morning-assistant/bundle-manifest.json',{'format':'instruction-bundle/1','main':'instruction.md','complete':False,'entries':entries,'mapping':mapping})
    print(f'Generated {len(cases)} model cases, {len(sources)} source checks, {len(text_cases)} text vectors and exchange/bundle examples.')
if __name__=='__main__':main()
