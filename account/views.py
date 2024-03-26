from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.http import HttpResponse
import random
import string
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Comment
from .utils import translate_to_english, detect_cyberbullying
from googletrans import Translator
import pickle
from django.views.generic import TemplateView
# Create your views here.

class Home(TemplateView):
    template_name='mainhome.html'

def home(request):
    # Logic to fetch posts
    posts = [
        {"title": "Post Title 1", "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."},
        {"title": "Post Title 2", "content": "Donec consectetur, ipsum et viverra sodales, nisi metus aliquet nisl."}
    ]
    return render(request, 'home.html', {'posts': posts})
def post(request):
    return render(request,'post.html')

def register(request):
    if request.method == 'POST':
        # Get form data
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
            return redirect('register')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered.')
            return redirect('register')
        else:
            # Validate email format
            if '@' not in email:
                messages.error(request, 'Invalid email format.')
                return redirect('register')
            
            # Validate password length (minimum 6 characters)
            if len(password) < 6:
                messages.error(request, 'Password must be at least 6 characters long.')
                return redirect('register')

            # Create new user
            user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
            user.save()

            # Automatically log in the user after registration
            auth_login(request, user)

            messages.success(request, 'You are now registered and logged in.')
            return redirect('login')  # Redirect to the login page or any desired page
    else:
        return render(request, 'register.html')
    



def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # User authentication successful, log in the user
            login(request, user)
            return redirect('h')  # Redirect to the home page after login
        else:
            # Invalid login credentials
            return render(request, 'login.html', {'error_message': 'Invalid username or password'})

    return render(request, 'login.html')


def profile(request):
    # Retrieve the logged-in user's data
    user = request.user

    # Pass the user data to the template
    context = {'user': user}
    return render(request, 'profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Get the current user
        user = request.user

        # Update user profile data with the form data
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')

        # Save the updated user profile data
        user.save()

        # Show success message
        messages.success(request, 'Profile updated successfully.')

        # Redirect to the profile page or any other page
        return redirect('profile')
    else:
        # Render the edit profile form with the current user data
        return render(request, 'edit_profile.html', {'user': request.user})
    
    
@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        user = request.user

        # Check if the current password is correct
        if not user.check_password(current_password):
            messages.error(request, 'Incorrect current password.')
            return redirect('change_password')

        # Check if new passwords match
        if new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
            return redirect('change_password')

        # Change the user's password
        user.set_password(new_password1)
        user.save()

        # Update the user's session hash to prevent logout
        update_session_auth_hash(request, user)

        messages.success(request, 'Your password has been successfully updated.')
        return redirect('profile')  # Redirect to profile page or any other desired page

    return render(request, 'change_password.html')



def generate_otp(length=6):
    """Generate a random OTP of specified length."""
    characters = string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return HttpResponse("No user with this email exists.")
        
        # Generate OTP
        otp = generate_otp()

        # Update user's profile with OTP (You might want to create a profile model)
        user.otp = otp
        user.save()

        # Send OTP via email
        subject = 'Password Reset OTP'
        message = f'Your OTP for password reset is: {otp}'
        from_email = 'pchinchu003@gmail.com'  # Update this with your email
        recipient_list = [email]
        send_mail(subject,message,from_email,recipient_list)

        return HttpResponse("An OTP has been sent to your email. Please check your inbox.")
    else:
        return render(request, 'forgot_password.html')
    

def login_with_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = request.POST.get('otp')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return HttpResponse("No user with this email exists.")

        # Verify OTP
        if user.otp == otp:
            # Login the user
            login(request, user)
            return HttpResponse("Logged in successfully with OTP.")
        else:
            return HttpResponse("Invalid OTP. Please try again.")
    else:
        return render(request, 'login_with_otp.html')
    
    
    


@login_required
def add_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')  # Assuming you have file input for image
        author = request.user

        # Create and save the new post
        new_post = Post(title=title, content=content, image=image, author=author)
        new_post.save()

        # Redirect to a success page or any other page after adding the post
        return redirect('view_posts')  # Redirect to post detail page , pk=new_post.pk
    else:
        # Render the add post form template if it's a GET request
        return render(request, 'addpost.html')
    
            


def add_comment(request, post_id):
    if request.method == 'POST':
        # Get the post object based on the post_id
        user=request.user
        post = get_object_or_404(Post, pk=post_id)
        
        # Get the comment body from the form submission
        body = request.POST.get('body')
        
        # Create a new comment object
        comment = Comment.objects.create(post=post, body=body, name=request.user)
        print(comment.body)
        # c=detect_cyberbullying(comment.body)
        # print(c)
        # Get the input text from the form
        text = comment.body
        # Load the TF-IDF vectorizer and the model
        with open('tfidf_vectorization', 'rb') as f:
            tfidf = pickle.load(f)
        with open('model', 'rb') as f:
            model = pickle.load(f)
        # Preprocess the text (similar to what you did before)
        # Vectorize the text
        text = tfidf.transform([text])
        # Make predictions
        prediction = model.predict(text)

        print(prediction)   
        if prediction == 1:
        
            # Define email parameters
            subject = 'Warning: Cyberbullying Detected'
            message = 'Your comment has been detected as containing cyberbullying. Please refrain from such behavior.'
            from_email = 'pchinchu003@gmail.com'
            recipient_list = [user.email]
            
            # Send the email
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            
            # Increment the warning count
            profile, created = Profile.objects.get_or_create(user=user)
        
            profile.warnings += 1
            profile.save()
            
            # Check if the user has been warned before
            if profile.warnings >= 2:
                user_data={
                    'username':user.username,
                    'email':user.email,
                }
                # Remove the user
                user.delete()
                
                # Send an email to the police station
                police_subject = 'Cyberbullying Report:Requesting Police Intervention'
                police_message = f'A user has been detected for cyberbullying and has been deleted from POSTGRAM website.\n\nUser Data:\n{user_data}'
                police_recipient = 'chinchuofficialweb@gmail.com'  # Replace with actual police email
                send_mail(police_subject, police_message, from_email, [police_recipient], fail_silently=False)
                return redirect(reverse('home'))
                
        # Redirect to the same page after adding the comment
        return redirect(reverse('view_posts'))
    
    
def view_posts(request, post_id=None):
    if post_id:
        # Fetch the specific post and its comments
        post = get_object_or_404(Post, pk=post_id)
        posts=[post]
        comments = post.comments.all()
    else:
        # Fetch all posts and their comments if no specific post_id is provided
        posts = Post.objects.all()
        comments = Comment.objects.all()
    
    context = {
        'posts': posts,
        'comments': comments,
    }
    return render(request, 'view_post.html', context)


    

def logout_view(request):
    logout(request)
    # Redirect to a specific URL after logout
    return redirect('home') 




@csrf_exempt
def translate_comment(request, comment_id):
    if request.method == 'GET':
        try:
            comment = Comment.objects.get(id=comment_id)
            translated_text = translate_to_english(comment.body)
            return JsonResponse({'translated_text': translated_text})
        except Comment.DoesNotExist:
            return JsonResponse({'error': 'Comment not found'}, status=404)
        



