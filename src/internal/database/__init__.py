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
