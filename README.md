# C2DB bandstructures
Download monlayer band structures from [C2DB](https://cmrdb.fysik.dtu.dk/c2db/) 

### Requirements
  - database: c2db.db
  - python (version >=3.0)

### Usage
  - c2dbjson.py:  A C2DBjson class is created,  [uid](https://cmr.fysik.dtu.dk/c2db/c2db.html#id8) is needed to specify the wanted layer material system.  
  - crawlC2DB.py: c2db.db is required to provide the uids, and it exhaustively searches all uids and download the band structure, materials structures, space group...
