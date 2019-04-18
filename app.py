from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields, pprint

app= Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///restaurants.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Menusection(db.Model):
	__tablename__ = 'menusection'
	id=db.Column(db.Integer,primary_key=True)
	name=db.Column(db.String(20),unique=True,nullable=False)
	Items=db.relationship('Sectionitems',backref='menuSection',lazy=True)

		


class Sectionitems(db.Model):
	__tablename__ = 'sectionitems'
	id=db.Column(db.Integer,primary_key=True)
	name=db.Column(db.String(20),unique=True,nullable=False)
	price=db.Column(db.Integer,nullable=False)
	m_id=db.Column(db.Integer,db.ForeignKey('menusection.id',ondelete='CASCADE'))
	Options=db.relationship('Itemoptions',backref='sectionItem',lazy=True)


class Itemoptions(db.Model):
	__tablename__ = 'itemoptions'
	id=db.Column(db.Integer,primary_key=True)
	name=db.Column(db.String(20),unique=True,nullable=False)
	price=db.Column(db.Integer,nullable=False)
	s_id=db.Column(db.Integer,db.ForeignKey('sectionitems.id',ondelete='CASCADE'))
	Choices=db.relationship('Itemchoices',backref='itemchoice',lazy=True)



class Itemchoices(db.Model):
	__tablename__ = 'itemchoices'
	id=db.Column(db.Integer,primary_key=True)
	name=db.Column(db.String(20),unique=True,nullable=False)
	price=db.Column(db.Integer,nullable=False)
	io_id=db.Column(db.Integer,db.ForeignKey('itemoptions.id',ondelete='CASCADE'))
	
	
class MenusectionSchema(Schema):
	id=fields.Integer()
	name=fields.String()
	Items=fields.Nested('SectionitemsSchema',many=True)
	class meta:
		fields=('id','name','Items')

			
	
		
	
class SectionitemsSchema(Schema):
	id=fields.Integer()
	name=fields.String()
	price=fields.Integer()
	Options=fields.Nested('ItemoptionsSchema',many=True)
	class Meta:
		fields=('id','name','price','Options')
	
	
class ItemoptionsSchema(Schema):
	id=fields.Integer()
	name=fields.String()
	price=fields.Integer()
	Choices=fields.Nested('ItemchoicesSchema',many=True)
	class Meta:
		fields=('id','name','price','Choices')



class ItemchoicesSchema(Schema):
	id=fields.Integer()
	name=fields.String()
	price=fields.Integer()
	class Meta:
		fields=('id','name','price')



@app.route('/menusection')
def getmenuSectionAll():
	menus=Menusection.query.all()
	menuSection_schema=MenusectionSchema(many=True)
	output=menuSection_schema.dump(menus).data
	return jsonify({'menusection':output})


@app.route('/menusection/<int:pk>')
def getmenuSectionById(pk):
	try:
		menu=Menusection.query.get(pk)

	except IntegrityError:
		return jsonify({'message':'could not be found'}),400
	menuSection_schema=MenusectionSchema()
	output=menuSection_schema.dump(menu).data
	return jsonify({'menu':output})


@app.route('/menusection',methods=['POST'])
def addNewMenu():
	json_data= request.get_json(force=True)
	pprint(json_data)
	if not json_data:
		return {"message':'No input data provided"},400

	menuSection_schema=MenusectionSchema()
	data= menuSection_schema.load(json_data).data
   

	if data['name'] is None:
		return {"message':'Needs menuSection name"},422
	name=data['name']
	menu=Menusection.query.filter_by(name=name).first()
	if menu is None:
		if data.get('Items') is None:
			menu=Menusection(name=name)
			db.session.add(menu)

		else:
			menu=Menusection(name=name)
			db.session.add(menu)
			for key in data['Items']:
				item=Sectionitems(name=key['name'],price=key['price'])
				if data['Items']['Options'] is None:
					db.session.add(item)
					menu.Items.append(item)

				else:
					db.session.add(item)
					menu.Items.append(item)
					for key in data['Items']['Options']:
						option=Itemoptions(name=key['name'],price=key['price'])
						if data['Items']['Options']['Choices'] is None:
							db.session.add(option)
							item.Options.append(option)

						else:
							db.session.add(option)
							item.Options.append(option)
							for key in data['Items']['Options']['Choices']:
								choice=Itemchoices(name=key['name'],price=key['price'])
								db.session.add(choice)
								option.Choices.append(choice)
	else:
		for key in data.get('Items'):
			item=Sectionitems(name=key['name'],price=key['price'],m_id=menu.id)
			db.session.add(item)
			

	db.session.commit()
	result=menuSection_schema.dump(Menusection.query.get(menu.id))
	return jsonify({'success':True,'menusection':result})
	

	
	
@app.route('/updateMenusection',methods=['post'])
def updateMenu():
	json_data=request.get_json(force=True)
	pprint(json_data)
	if not json_data:
		return {"message':'No input data provided"},400

	menuSection_schema=MenusectionSchema()
	data= menuSection_schema.load(json_data).data
	menu=Menusection.query.filter_by(id=data['id']).first()
	if not menu:
		return {'message':'Menu does not exist'},400

	menu.name=data['name']
	db.session.commit()
	result=menuSection_schema.dump(Menusection.query.get(menu.id))
	return jsonify({'success':True,'menu':result})	
   

	
@app.route('/updateSection',methods=['post'])
def updateSection():
	json_data=request.get_json(force=True)
	pprint(json_data)
	if not json_data:
		return {"message':'No input data provided"},400

	sectionItems_schema=SectionitemSchema()
	data= sectionItems_schema.load(json_data).data
	item=Sectionitems.query.filter_by(id=data['id']).first()
	if not item:
		return {'message':'Menu does not exist'},400

	item.name=data['name']
	db.session.commit()
	result=sectionItems_schema.dump(Sectionitems.query.get(item.id))
	return jsonify({'success':True,'item':result})	
	
			
			
		
	

@app.route('/menusection/<int:pk>',methods=['DELETE'])
def deleteMenu(pk):
	menu=Menusection.query.filter_by(id=pk).first()
	pprint(menu)
	if menu is None:
		return {"message":"No record related to ID"}

	else:	

		db.session.delete(menu)
		db.session.commit()
		return jsonify({'success':True})
		
	
				

if __name__ == '__main__':
	app.run(debug=True)	    		


		
		
	
 
	
