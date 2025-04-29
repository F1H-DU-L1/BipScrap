from flask import Flask, request, jsonify
from db.models import Base, Document, DocumentFullVersion
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

engine = create_engine('postgresql://postgres:postgres@localhost/bip_indexing')
Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

@app.route('/uploadfulldoc', methods=['POST'])
def upload_document():
    data = request.get_json()
    source_url = data.get("source_url")
    content = data.get("content")

    if not source_url or not content:
        return jsonify({"error": "Missing source_url or content"}), 400

    session = Session()

    try:
        # Search for URL
        document = session.query(Document).filter_by(url=source_url).first()

        if not document:
            #if unique document source url then add new document
            document = Document(url=source_url)
            session.add(document)
            session.flush()
            
        #always add new version
        full_version = DocumentFullVersion(
            document_id=document.document_id,
            content=content
        )
        session.add(full_version)
        session.commit()

        return jsonify({"message": "Document saved"}), 200

    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        session.close()
        
if __name__ == "__main__":
    app.run(debug=True)
