# simple-face-auth

⚠️ For educational purposes only

Python 3.10

## Start
Linux: make sure that <i>build-essential</i> tools are installed

```bash
 sudo apt-get install build-essential
```

Windows: since this application depends on the <i>face-recognition</i> library, Windows users should probably take a look here:
https://github.com/ageitgey/face_recognition/issues/175#issue-257710508

### Install dependencies

```bash
 pip install -r requirements.txt  
```

### Run migrations
```bash
 alembic upgrade head 
```

### Execute main
Navigate to /app folder and execute main.py script

```bash
 python main.py
```