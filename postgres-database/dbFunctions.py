# dbFunctions.py [Rachel Gardner]
#
# This file defines the AcronymsDatabase class, which
# interfaces with the PostgreSQL backend to store acronyms, definitions
# and their contexts.

import psycopg2
import json
from collections import Counter

class AcronymDatabase:
    def __init__(self):
        conn = psycopg2.connect(database="acronyms", user="acronym_user", password="cs221", host="localhost")
        self.conn = conn
        self.cur = conn.cursor()

    def addAcronym(self, acronym):
        self.cur.execute("INSERT INTO acronyms (acronym) VALUES (%s) RETURNING aid", (acronym,))
        return self.cur.fetchone()[0]

    def getAcronym(self, acronym):
        self.cur.execute("SELECT aid FROM acronyms WHERE acronym=%s", (acronym,))
        result = self.cur.fetchone()
        return result[0] if result else None

    def addDefinition(self, definition, context, url, aID = False):
        self.cur.execute("INSERT INTO definitions (definition, context, url) VALUES (%s, %s, %s) RETURNING did", (definition,context, url))
        dID = self.cur.fetchone()[0]

        # if acronym exists, link this definition to existing acronym
        if (aID):
            self.cur.execute("INSERT INTO acronyms_definitions (aid, did) VALUES (%s, %s)", (aID, dID))
        
        return dID

    def addTrueDefinition(self, acronym, truedef, url):
        self.cur.execute("SELECT true_definition FROM true_definitions WHERE acronym=%s AND url=%s", (acronym,url))
        result = self.cur.fetchone()
        if(not result): result = None
        else: result=result[0]
        if(result is None):
            self.cur.execute("INSERT INTO true_definitions (acronym, true_definition, url) VALUES (%s, %s, %s)", (acronym,truedef,url))

    def getTrueDefinition(self, acronym, url):
        self.cur.execute("SELECT true_definition FROM true_definitions WHERE acronym=%s AND url=%s", (acronym,url))
        result = self.cur.fetchone()
        return result[0] if result else None

    
    def addContext(self, context):
        self.cur.execute("INSERT INTO context (context) VALUES (%s) RETURNING cid", (context,))
        return self.cur.fetchone()[0]

    def acronymHasDefinition(self,aID, definition):
        self.cur.execute("SELECT definitions.DID from definitions JOIN acronyms_definitions ON acronyms_definitions.DID = definitions.DID WHERE definitions.definition = %s AND acronyms_definitions.AID = %s", (definition, aID))
        result = self.cur.fetchone()
        return result[0] if result else None

    def addContext(self,definition_id, context):
        newContextJSON = json.dumps(context)
        self.cur.execute("UPDATE context SET context=%s FROM definitions WHERE DID=%s", (newContextJSON,definition_id))

    def updateContext(self, definition_id, context):
        self.cur.execute("SELECT context FROM definitions JOIN context ON definitions.CID = context.CID WHERE DID = %s LIMIT 1;", (definition_id,))
        oldContextJSON = self.cur.fetchone()[0]
        oldContext = Counter(json.loads(oldContextJSON))
        newContext = oldContext + context
        newContextJSON = json.dumps(newContext)
        self.cur.execute("UPDATE context SET context=%s FROM definitions WHERE DID=%s", (newContextJSON,definition_id))

    def getContextAcronymList(self):
        self.cur.execute("SELECT did, context, definition FROM definitions")
        result = self.cur.fetchall()
        ret = []
        for elem in result:
            did = str(elem[0])
            self.cur.execute("SELECT aid FROM acronyms_definitions WHERE did=%s" ,(did,))
            aid = str(self.cur.fetchone()[0])
            self.cur.execute("SELECT acronym FROM acronyms WHERE aid=%s", (aid,))
            acronym = self.cur.fetchone()[0]
            ret.append((acronym, elem[1], elem[2]))
        return ret

    def clearTrueDefTable(self):
        self.cur.execute("DELETE FROM true_definitions")

    def clearAcronymTables(self):
        self.cur.execute("DELETE FROM definitions")
        self.cur.execute("DELETE FROM acronyms")
        self.cur.execute("DELETE FROM acronyms_definitions")

    def close(self):
        self.conn.commit()  # make the changes to the database persistent
        self.cur.close()
        self.conn.close()
