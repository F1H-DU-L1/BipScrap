from flask import Flask, request, jsonify
from db.models import Base, DocumentFull , DocumentDiff , LLM
from sqlalchemy import create_engine, select, desc
from sqlalchemy.orm import sessionmaker
from datetime import datetime

app = Flask(__name__)

engine = create_engine('postgresql://postgres:postgres@localhost/bip_indexing')
Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

#Team 1 endpoint for upload
@app.route('/uploadfulldoc', methods=['POST'])
def upload_document():
    data = request.get_json()
    base_url = data.get("base_URL")
    scrap_datetime_string = data.get("scrap_datetime")
    url = data.get("URL")
    content = data.get("Content")

    if not(base_url and scrap_datetime_string and url and content):
        return jsonify({"error": "Missing data"}), 400

    session = Session()

    try:
        try:
            scrap_datetime_parsed = datetime.fromisoformat(scrap_datetime_string)
        except ValueError:
            return jsonify({"error": "Invalid datetime format. Use ISO 8601."}), 400
        full_version = DocumentFull(
            base_url = base_url,
            scrap_datetime = scrap_datetime_parsed,
            url = url,
            content = content
        )
        session.add(full_version)
        session.commit()

        return jsonify({"message": "Document saved successfully"}), 200

    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        session.close()

#Team 2 endpoint for getting the latest 2 docs
@app.route('/getdocs', methods=['POST'])
def getdocs():
    data = request.get_json()
    docs_url = data.get("URL")
    if not docs_url:
        return jsonify({"error":"Missing url"}), 400
    
    session = Session()
    try:
        query = (select(DocumentFull.content)
                 .where(DocumentFull.url==docs_url)
                 .order_by(desc(DocumentFull.scrap_datetime))
                 .limit(2))
        result = session.execute(query).scalars().all()
        
        if len(result) > 1:
            return jsonify({"Latest doc": result [0], "Second latest doc": result [1]}), 200
        elif len(result) == 1:
            return jsonify({"Latest doc": result [0], "Second latest doc": None}), 200
        else:
            return jsonify({"error": "No docs matching this url yet"}), 404
        
    except Exception as e:
        session.rollback()
        return jsonify({"error":str(e)}), 500
    
    finally:
        session.close()

if __name__ == "__main__":
    app.run(debug=True)