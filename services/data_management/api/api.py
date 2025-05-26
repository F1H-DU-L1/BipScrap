import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from db.models import Base, DocumentFull , DocumentDiff , LLM
from sqlalchemy import create_engine, select, desc
from sqlalchemy.orm import sessionmaker
from datetime import datetime

app = Flask(__name__)
load_dotenv( )

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

#Team 1 endpoint for upload
@app.route('/fulldoc', methods=['POST'])
def upload_document():
    data = request.get_json()
    base_url = data.get("base_url")
    scrap_datetime_string = data.get("scrap_datetime")
    url = data.get("url")
    content = data.get("content")

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
# todo return also doc_id_key
@app.route('/docs', methods=['GET'])
def getdocs():
    data = request.get_json()
    docs_url = data.get("url")
    if not docs_url:
        return jsonify({"error":"Missing url"}), 400
    
    session = Session()
    try:
        query = (select(DocumentFull.content, DocumentFull.doc_id)
                 .where(DocumentFull.url==docs_url)
                 .order_by(desc(DocumentFull.scrap_datetime))
                 .limit(2))
        result = session.execute(query).mappings().all()
        
        #prepare the list to be sent
        documents = []
        if result:
            documents.append(dict(result[0]))
            if len(result)>1:
                documents.append(dict(result[1]))
            else:
                documents.append(None)
            #if there are results send the docs
            return jsonify({"documents": documents}), 200
        #otherwise send error
        else:
            return jsonify({"error": "No docs matching this url yet"}), 404
        
    except Exception as e:
        session.rollback()
        return jsonify({"error":str(e)}), 500
    
    finally:
        session.close()

# Team 2: diff saving
@app.route('/diff', methods=['POST'])
def save_diff():
    data = request.get_json()
    doc_id_key_1 = data.get("doc_id_key_1")
    doc_id_key_2 = data.get("doc_id_key_2")
    content = data.get("content")
    if not (doc_id_key_1 and doc_id_key_2):
        return jsonify({"error":"Missing doc_id_key"}), 400
    if not content:
        return jsonify({"error":"Missing content"}), 400
    
    session = Session()
    try:
        diff = DocumentDiff(
            doc_id_key_1=doc_id_key_1,
            doc_id_key_2=doc_id_key_2,
            content=content
        )
        session.add(diff)
        session.commit()
        return jsonify({"message": "Document saved successfully", "doc_diff_id": diff.doc_diff_id}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

# Team 3: diff getting
@app.route('/diff/<int:doc_diff_id>', methods=['GET'])
def get_diff(doc_diff_id):
    if not doc_diff_id:
        return jsonify({"error":"Missing doc_diff_id"}), 400
    session = Session()
    try:
        query = (select(DocumentDiff.content)
                 .where(DocumentDiff.doc_diff_id==doc_diff_id))
        result = session.execute(query).scalars().all()
        
        if len(result) > 0:
            return jsonify({"content": result[0]}), 200
        else:
            return jsonify({"error": "No diff found for this ID"}), 404
        
    except Exception as e:
        session.rollback()
        return jsonify({"error":str(e)}), 500
    
    finally:
        session.close()
    
# Team 3: LLM output saving
@app.route('/summary/<int:doc_diff_id>', methods=['POST'])
def save_summary(doc_diff_id):
    data = request.get_json()
    llm_summary = data.get("content")
    if not llm_summary:
        return jsonify({"error":"Missing content"}), 400
    
    session = Session()
    try:
        llm_output = LLM(
            doc_diff_id=doc_diff_id,
            base_url=obatin_base_url(doc_diff_id),
            content=llm_summary,
            date_time=datetime.now()
        )
        session.add(llm_output)
        session.commit()
        return jsonify({"message": "Summary saved successfully", "llm_id": llm_output.LLM_id}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

def obatin_base_url(doc_diff_id: str) -> str:
    """
    Function to obtain the base URL from the full document
    """
    session = Session()
    try:
        query = (select(DocumentFull.base_url)
                    .join(DocumentDiff, DocumentFull.doc_id==DocumentDiff.doc_id_key_1)
                    .where(DocumentDiff.doc_diff_id==doc_diff_id))
                
        result = session.execute(query).scalars().all()
        
        if not result or len(result) == 0:
            return ""
        else:
            return result[0]
        
    except Exception as e:
        session.rollback()
        return ""
    
    finally:
        session.close()

if __name__ == "__main__":
    app.run(debug=True)
