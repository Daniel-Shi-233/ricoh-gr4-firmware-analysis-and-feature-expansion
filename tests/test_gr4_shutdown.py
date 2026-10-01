"""Finite TTL control-flow model. Not a camera interpreter or storage emulator."""
import shlex
import struct
import unittest
import tempfile
from pathlib import Path
from tools.gr4_model import MODELS
from tools.gr4_shutdown import generate_backup, generate_write, BACKUPS, prepare, verify

def run(script, fs, fail_copy=None):
 lines=script.splitlines();labels={s[1:]:i for i,s in enumerate(lines) if s.startswith(':')}
 v={};handles={};pc=0;include=False;count=0;copies=0
 def val(x):
  if x in v:return v[x]
  try:return int(x)
  except ValueError:return x
 while pc<len(lines):
  count+=1;assert count<30000
  s=lines[pc].strip();pc+=1
  if not s or s.startswith((';',':')):continue
  a=shlex.split(s,posix=True);op=a[0]
  if op=='if':
   l,r=val(a[1]),val(a[3]);ok={'=':lambda:l==r,'<>':lambda:l!=r,'<':lambda:l<r,'>':lambda:l>r,'>=':lambda:l>=r}[a[2]]()
   if not ok:
    depth=1
    while depth:
     t=lines[pc].strip();pc+=1
     if t.startswith('if '):depth+=1
     elif t=='endif':depth-=1
   continue
  if op=='endif':continue
  if op=='goto':pc=labels[a[1]];continue
  if op=='exit':break
  if len(a)>1 and a[1]=='=':v[a[0]]=val(a[2])+(val(a[4]) if len(a)>4 else 0) if len(a)>4 else val(a[2]);continue
  if op=='filesearch':v['result']=int(val(a[1]) in fs)
  elif op=='filestat':v[a[2]]=len(fs[val(a[1])]) if val(a[1]) in fs else -1
  elif op=='int2str':v[a[1]]=str(val(a[2]))
  elif op=='str2code':v[a[1]]=ord(val(a[2])[0]) if val(a[2]) else 0
  elif op=='str2int':v[a[1]]=int(val(a[2]).strip())
  elif op=='strconcat':v[a[1]]+=str(val(a[2]))
  elif op=='strcopy':v[a[4]]=val(a[1])[int(a[2])-1:int(a[2])-1+int(a[3])]
  elif op=='strcompare':v['result']=0 if str(val(a[1]))==str(val(a[2])) else 1
  elif op=='filecopy':
   copies+=1
   if copies!=fail_copy:fs[val(a[2])]=fs.get(val(a[1]),b'')
  elif op in ['fileopen','filecreate']:
   name=val(a[2]);v[a[1]]=len(handles)+1 if op=='filecreate' or name in fs else -1
   if v[a[1]]>=0:handles[v[a[1]]]=[name,0]
   if op=='filecreate':fs[name]=b''
  elif op=='fileclose':handles.pop(val(a[1]),None)
  elif op=='filewrite':fs[handles[val(a[1])][0]]+=str(val(a[2])).encode()
  elif op=='fileread':
   h=handles[val(a[1])];n=int(a[2]);v[a[3]]=fs[h[0]][h[1]:h[1]+n].decode('latin1');h[1]+=n
  elif op=='include':include=True;break
  else:raise ValueError(s)
 return include,copies

class WorkflowTests(unittest.TestCase):
    def test_all_models_backup_replace_restore_and_repeat(self):
        for product,(model,target) in MODELS.items():
            with self.subTest(model=model):
                fs={r'E:\BlkCtl15.bin':struct.pack('<II',0xA55A5AA5,product),target:b'original'}
                run(generate_backup(),fs)
                backup='C:\\'+BACKUPS[model]
                self.assertEqual(fs[backup],b'original')
                fs[r'C:\NEWGB.JPG']=b'newimage';fs[r'C:\GBARM.TXT']=b'1'
                run(generate_write(model,8),fs)
                self.assertEqual(fs[target],b'newimage')
                self.assertEqual(fs[r'C:\GBREAD.JPG'],b'newimage')
                del fs[r'C:\GBREAD.JPG']
                self.assertEqual(run(generate_write(model,8),fs)[1],0)
                run(generate_backup(),fs);self.assertEqual(fs[backup],b'original')
                fs[r'C:\GBARM.TXT']=b'1'
                run(generate_write(model,8,True),fs)
                self.assertEqual(fs[target],b'original')
                self.assertEqual(fs[r'C:\GBREST.JPG'],b'original')

    def test_wrong_model_unknown_header_and_copy_failure(self):
        target=MODELS[0x132E0][1]
        fs={r'E:\BlkCtl15.bin':struct.pack('<II',0xA55A5AA5,0x132E0), target:b'original',r'C:\GBSTD.JPG':b'original',r'C:\NEWGB.JPG':b'newimage',r'C:\GBARM.TXT':b'1'}
        self.assertEqual(run(generate_write('MONO',8),fs)[1],0)
        run(generate_write('STANDARD',8),fs,1)
        self.assertEqual(fs[target],b'original')
        self.assertEqual(fs[r'C:\GBARM.TXT'],b'0')
        self.assertEqual(run(generate_backup(),{r'E:\BlkCtl15.bin':b'\0'*8})[1],0)

    def test_prepare_and_full_readback(self):
        from PIL import Image
        from tools.pad_jpeg import pad_jpeg
        from io import BytesIO
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);card=root/'card';card.mkdir()
            im=Image.new('RGB',(720,480),'white');b=BytesIO();im.save(b,format='JPEG')
            original=pad_jpeg(b.getvalue(),20000)
            (card/'GBMODEL.TXT').write_text('HDF');(card/'GBHDF.JPG').write_bytes(original)
            image=root/'input.png';im.save(image)
            package=root/'package';prepare(card,image,package)
            verify(package,package/'NEWGB.JPG')
            verify(package,package/'GBHDF.JPG',True)
            bad=root/'bad.jpg';bad.write_bytes(b'x'*20000)
            with self.assertRaises(ValueError):verify(package,bad)
            with self.assertRaises(ValueError):prepare(card,image,package)


class SimpleTemplateTests(unittest.TestCase):
    def test_three_models_single_image_and_restore(self):
        from tools.gr4_shutdown import generate_simple_write
        for product,(model,target) in MODELS.items():
            fs={r'E:\BlkCtl15.bin':struct.pack('<II',0xA55A5AA5,product),target:b'original'}
            run(generate_backup(),fs)
            fs[r'C:\NEWGB.JPG']=b'newimage'
            run(generate_simple_write(),fs)
            self.assertEqual(fs[target],b'newimage')
            self.assertEqual(fs[r'C:\GBREAD.JPG'],b'newimage')
            self.assertEqual(run(generate_simple_write(),fs)[1],0)
            run(generate_simple_write(True),fs)
            self.assertEqual(fs[target],b'original')
            self.assertEqual(fs[r'C:\GBREST.JPG'],b'original')

    def test_failed_attempt_not_retried_and_wrong_length_rejected(self):
        from tools.gr4_shutdown import generate_simple_write
        target=MODELS[0x132E0][1]
        fs={r'E:\BlkCtl15.bin':struct.pack('<II',0xA55A5AA5,0x132E0),target:b'original'}
        run(generate_backup(),fs)
        fs[r'C:\NEWGB.JPG']=b'short'
        self.assertEqual(run(generate_simple_write(),fs)[1],0)
        fs[r'C:\NEWGB.JPG']=b'newimage'
        run(generate_simple_write(),fs,1)
        self.assertEqual(fs[target],b'original')
        self.assertEqual(run(generate_simple_write(),fs)[1],0)

    def test_checked_in_templates_match_generator(self):
        from tools.gr4_shutdown import generate_simple_write
        root=Path(__file__).resolve().parents[1]/'examples'
        for phase,text in [('backup',generate_backup()),('write',generate_simple_write()),('restore',generate_simple_write(True))]:
            self.assertEqual((root/f'{phase}-gr4-family.ttl.example').read_text(),'; License: see LICENSE\n'+text)
