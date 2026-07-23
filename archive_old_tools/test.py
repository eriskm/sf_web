import sys
sys.path.append('f:/SFS PROJECK/SF_WEB')
import app
ctx = app.app.test_request_context('/generate_nota_image/68?garansi=1Bulan')
ctx.push()
try:
    res = app.generate_nota_image(68)
    print("RESULT:", type(res))
except Exception as e:
    import traceback
    traceback.print_exc()
