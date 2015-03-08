from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth import authenticate, login
from django.contrib.auth import logout

from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse

from django.shortcuts import redirect

from rango.models import Category, Page
from rango.models import UserProfile

from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm

from rango.bing_search import run_query


from datetime import datetime


def index(request):


    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {'categories': category_list, 'pages': page_list}

    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).seconds > 0:
            # ...reassign the value of the cookie to +1 of what it was before...
            visits = visits + 1
            # ...and update the last visit cookie, too.
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so create it to the current date/time.
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits


    response = render(request,'rango/index.html', context_dict)

    return response

	

def about(request):

    # If the visits session varible exists, take it and use it.
# If it doesn't, we haven't visited the site so set the count to zero.
    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0

    # remember to include the visit data

    context_dict = {'jaakko': "This tutorial has been put together by Jaakko Alasuvanto, 2160057"}
    context_dict['visits'] = count

    return render(request, 'rango/about.html', context_dict)

def category(request, category_name_slug):
    context_dict = {}
    context_dict['result_list'] = None
    context_dict['query'] = None
    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

            context_dict['result_list'] = result_list
            context_dict['query'] = query

    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        pass

    if not context_dict['query']:
        context_dict['query'] = category.name

    return render(request, 'rango/category.html', context_dict)

@login_required
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

@login_required
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

"""
def user_login(request):

    login_failed = False

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled. 
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            login_failed = True
            # How to use HttpRequestRedirect here???????????????????????????????????????????????????
            return render(request, 'rango/login.html', {'login_failed':login_failed}) 

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'rango/login.html', {'login_failed':login_failed}) 
"""
@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})

"""
@login_required
def user_logout(request):
    logout(request)

    return HttpResponseRedirect('/rango/')
    """


def search(request):

    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})

def track_url(request):

    url = '/rango/'
    page_id = None

    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass



    return redirect(url)

def register_profile(request):



    context_dict = {}



    if request.method == 'POST':
        
        profile_form = UserProfileForm(request.POST)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            user = User.objects.get(id=request.user.id)
            profile.user = user
            profile.picture = request.FILES.get('picture')
            profile.save()
            return HttpResponseRedirect('/rango/')

    else:
        profile_form = UserProfileForm(request.GET)
        context_dict['profile_form'] = profile_form
        return render(request, 'rango/profile_registration.html', context_dict)


@login_required
def profile(request, username):
    #How to edit??
    currentUser = User.objects.get(username=username)

    try:
        userProfile = UserProfile.objects.get(user = currentUser)
    except:
        userProfile = None

    return render(request, 'rango/profile.html', {'currentUser':currentUser, 'userProfile':userProfile})


def users(request):
    context_dict = {}
    users = User.objects.order_by('username')
    context_dict['users'] = users
    return render(request, 'rango/users.html', context_dict)


    """
def register(request):

    #Boolean value for telling the template if the registeration was succesful or not.
    # Set to false initially, changed to True when succesful registeration has occurred.



    registered = False

    if request.method == 'POST':

        #Grab the information from the raw for information
        user_form = UserForm(data = request.POST)
        profile_form = UserProfileForm(data = request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            #Save the user's form data to the database
            user = user_form.save()

            #Now we hash the password with set_password method
            #Once hashed, we can update the user object

            user.set_password(user.password)
            user.save()

            #Sorting out the UserProfile instance
            #Since we need to set the user attribute ourselves, we set commit=False
            #This delays saving the model until we're ready to avoid integrity problems.

            profile = profile_form.save(commit=False)
            profile.user = user

            #Was a picture submitted?
            #We need to get it from the input form and put it in the UserProfile model
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()
            registered = True 
        else:
            print user_form.errors, profile_form.errors

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request,
        'rango/register.html',
        {'user_form':user_form, 'profile_form':profile_form, 'registered':registered} )
"""