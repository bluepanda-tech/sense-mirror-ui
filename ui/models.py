from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

Base = automap_base()

# instantiating the engine
#TODO add database URI from environment variable
engine = create_engine("postgresql://postgres:mysecretpassword@localhost/cime")

# reflect the tables
Base.prepare(engine, reflect=True)

# mapped classes are now created with names by default
# matching that of the table name.
Product = Base.classes.products
MediaFile = Base.classes.media_files
DeletedFile = Base.classes.deleted_files
ProductEdit = Base.classes.product_edits
ProductToDisplayInfo = Base.classes.info_to_display

session = Session(engine)
