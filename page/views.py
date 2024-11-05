from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import *
from django.db.models import Q
from .models import Student# Ensure this imports your Student model
import random
from .models import details 
import string
from django.utils import timezone
import json
import os
import re  # Import regex module



def index(request):
    students = Student.objects.all()  # Only active students
    return render(request, 'table.html', {'students': students})

def page(request):
    students = Student.objects.all()
    return render(request, 'table.html', {'students': students})


def generate_random_string(length=20):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))

def table(request):
    for _ in range(150):
        name = generate_random_string(10)  # Generate a random name
        age = random.randint(15, 30)
        address = generate_random_string(25)
        state = generate_random_string(10)
        created_at = timezone.now()
        updated_at = timezone.now()

        Student.objects.create(name=name, age=age, address=address, state=state, created_at=created_at, updated_at=updated_at)

    return redirect('your_view')  # Redirect to view after generating data

def display(request):
    students = Student.objects.all()
    return render(request, 'table.html', {'students': students})

def view_list(request):
    students = Student.objects.all()
    context = {
        'students': students
    }
    return render(request, 'table.html', context)


    
def your_view(request):
    # Retrieve sorting parameters from request
    sort_field = request.GET.get('sort', 'id')  # Default to 'id'
    sort_order = request.GET.get('order', 'asc')
    
    # Apply sorting based on the sort_order and sort_field
    order_by = sort_field if sort_order == 'asc' else f'-{sort_field}'
    
    # Search query handling (only searching by name)
    search_query = request.GET.get('search', '')
    students = Student.objects.all()
    
    if search_query:
        students = students.filter(name__icontains=search_query)  # Search only by name
    
    # Sort students based on order_by
    students = students.order_by(order_by)

    # Pagination
    paginator = Paginator(students, 10)  # Display 10 students per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Add sorting and search parameters to context for pagination links
    context = {
        'page_obj': page_obj,
        'sort_field': sort_field,
        'sort_order': sort_order,
        'search_query': search_query,
    }
    
    return render(request, 'table.html', context)


def soft_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.delete()  # This will set the deleted_at field
    return redirect('your_view')

def restore_view(request, pk):
    student = get_object_or_404(Student, pk=pk, deleted_at__isnull=False)  # Check if it's soft deleted
    student.deleted_at = None  # Restore the student by setting deleted_at to None
    student.save()
    return redirect('your_view')

def hard_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)  # Get the student or return 404
    student.delete()  # Permanently delete the record from the database
    return redirect('your_view')  # Redirect to an appropriate view

def search_students(request):
    if 'q' in request.GET:
        query = request.GET['q']
        students = Student.objects.filter(Q(name__icontains=query) | Q(address__icontains=query))
        results = [{'id': student.id, 'name': student.name} for student in students]
        return JsonResponse(results, safe=False)
    
    return JsonResponse([], safe=False)  # Return an empty list if no query is provided



# phase 2
# Define the path to your JSON file
JSON_FILE_PATH = os.path.join(os.path.dirname(__file__), 'students.json')

def load_students():
    if os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, 'r') as file:
            return json.load(file)
    return []

def save_students(students):
    with open(JSON_FILE_PATH, 'w') as file:
        json.dump(students, file, indent=4)

def index(request):
    students = load_students()
    return render(request, 'test.html', {'students': students})

def test(request):
    students = load_students()
    
    if request.method == 'POST':
        student_id = request.POST['student_id']
        name = request.POST['name']
        student_class = request.POST['student_class']
        mark = request.POST['mark']
        phone = request.POST['phone']
        
        # Validate phone number
        if not re.match(r'^\+?1?\d{9,15}$', phone):
            return render(request, 'test.html', {
                'students': students,
                'error': 'Invalid phone number format. Please enter a valid phone number.'
            })



        new_student = {
            'id': student_id,
            'name': name,
            'class': student_class,
            'mark': mark,
            'phone': phone
        }

        # Save to JSON
        students.append(new_student)
        save_students(students)

        # Save to database
        details.objects.create(student_id=student_id, name=name, student_class=student_class, mark=mark, phone=phone)

        return redirect('index')  # Redirect to index after saving

    return render(request, 'test.html', {'students': students})

def edit_student(request, student_id):
    """Edit an existing student's details."""
    students = load_students()
    student_to_edit = next((student for student in students if student['id'] == student_id), None)

    if request.method == 'POST':
        # Retrieve updated data from the form
        name = request.POST.get('name')
        student_class = request.POST.get('student_class')
        mark = request.POST.get('mark')
        phone = request.POST.get('phone')

        # Validate phone number format
        if not re.match(r'^\+?1?\d{9,15}$', phone):
            return render(request, 'edit.html', {
                'student': student_to_edit,
                'error': 'Invalid phone number format.'
            })

        # Update the student's details if found
        if student_to_edit:
            student_to_edit.update({
                'name': name,
                'class': student_class,
                'mark': mark,
                'phone': phone
            })
            save_students(students)  # Save updated students list to JSON
            
            # Update details in the database (if you have a model for it)
            try:
                details_obj = details.objects.get(student_id=student_id)
                details_obj.name = name
                details_obj.student_class = student_class
                details_obj.mark = mark
                details_obj.phone = phone
                details_obj.save()
            except details.DoesNotExist:
                return render(request, 'edit.html', {
                    'student': student_to_edit,
                    'error': 'Student not found in database.'
                })

            return redirect('index')  # Redirect after saving

    # Render edit form with current data for GET request
    return render(request, 'edit.html', {'student': student_to_edit})