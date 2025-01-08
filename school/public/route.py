from school import app,search
from flask import render_template,request
from school.admin.models import Post,Category

@app.route('/')
def index():
    page=request.args.get('page',1,type=int)
    post=Post.query.order_by(Post.id.desc()).paginate(page=page,per_page=4)
    categories=Category.query.join(Post,(Category.id==Post.category_id)).all()
    return render_template('/public/index.html',post=post,categories=categories)

@app.route('/result')
def result():
    categories=Category.query.join(Post,(Category.id==Post.category_id)).all()
    searchword=request.args.get('q')
    post=Post.query.msearch(searchword,fields=['title','content'],limit=6)
    return render_template('/public/result.html',post=post,categories=categories)

@app.route('/single_page/<int:id>')
def single_page(id):
    post=Post.query.get_or_404(id)
    return render_template('/public/single_page.html',post=post)
