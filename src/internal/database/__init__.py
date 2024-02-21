from pkg.firebase_tools.tools import (
    FirebaseTools,
    FirebaseAuthTools,
    FirebaseStorage,
    FirebaseAsunc,
)


firebase_app = FirebaseTools()
db = FirebaseAsunc()
auth = FirebaseAuthTools()
storage = FirebaseStorage()
# as_db = firebase_app.get_asunc_firebase_client()
