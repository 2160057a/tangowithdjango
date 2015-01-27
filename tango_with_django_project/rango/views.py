from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect

from django.core.urlresolvers import reverse

from rango.models import Category, Page

from rango.forms import CategoryForm, PageForm 


def index(request):
	category_list = Category.objects.order_by('-likes')[:5]

	most_viewed_pages = Page.objects.order_by('-views')[:5]
	context_dict = {'most_viewed_pages': most_viewed_pages, 'categories': category_list}

	return render(request, 'rango/index.html', context_dict)

	

def about(request):

	context_dict = {'jaakko': "This tutorial has been put together by Jaakko Alasuvanto, 2160057"}

	return render(request, 'rango/about.html', context_dict)

def category(request, category_name_slug):

	#Create the context dictionary to be passed for the render
	context_dict = {}

	try:
		#Can we find a category name slug with the given name?
		#If not, the .get() method raises a DoesNotExist exception
		#So the .get() method returns one model instance or raises hell
		category = Category.objects.get(slug = category_name_slug)
		context_dict['category_name'] = category.name

		#Retrieve all of the associated pages
		#NOTE!! Filter returns >= 1 model instances.
		pages = Page.objects.filter(category=category)

		#Adds our results list to template context
		context_dict['pages'] = pages

		#Also add the category objects from the database to the context dictionary.
		#We'll use this in the template to verify that the category exists.
		context_dict['category'] = category

		#Add category_name_slug to context_dict 
		context_dict['category_name_slug'] = category_name_slug

	except Category.DoesNotExist:
		#We get here if we didin't find the secified category
		#Don't do anything  the template displays the "no category" message for us.
		pass


	return render(request, 'rango/category.html', context_dict)


def add_category(request):
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})


def add_page(request, category_name_slug):

    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
                cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                # probably better to use a redirect here.
                return HttpResponseRedirect(reverse('category', args=[cat.slug]))
        else:
            print form.errors
    else:
        form = PageForm()

    context_dict = {'form':form, 'category': cat}

    return render(request, 'rango/add_page.html', context_dict)