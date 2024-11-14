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
from rest_framework import status
from rest_framework.views import APIView
from .serializers import StudentSerializer



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
    # if 'undo_option' in request.session:
    #     del request.session['undo_option']  # Clear after displaying once
    
    students = load_students()  # Load students from JSON file or database
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
        # Store current state in session for undo functionality
        request.session['undo_data'] = student_to_edit.copy()  # Save current state
        request.session['undo_option'] = True  # Set undo option flag
        print('undo_data')
        print(request.session['undo_data'])
        print('undo_option')
        print(request.session['undo_option'])

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

            # Update details in the database
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


def undo_edit(request):
    """Undo the last edit made to a student's details."""
    if 'undo_data' in request.session and request.session.get('undo_option'):
        previous_data = request.session['undo_data']

        # Load current students and find the one to restore
        students = load_students()
        student_to_restore = next((student for student in students if student['id'] == previous_data['id']), None)

        if student_to_restore:
            # Restore previous data
            student_to_restore.update(previous_data)
            save_students(students)  # Save restored students list to JSON

            # Optionally, update the database as well
            try:
                details_obj = details.objects.get(student_id=previous_data['id'])
                details_obj.name = previous_data['name']
                details_obj.student_class = previous_data['class']
                details_obj.mark = previous_data['mark']
                details_obj.phone = previous_data['phone']
                details_obj.save()
            except details.DoesNotExist:
                pass  # Handle error or log it

            del request.session['undo_data']  # Clear undo data after restoring
            del request.session['undo_option']  # Clear undo option flag
            
            

    return redirect('index')  # Redirect after undoing


#using api for student management


class StudentListCreate(APIView):
    """
    List all students or create a new student.
    """
    # Define a method to handle GET requests to retrieve a list of all students
    def get(self, request):
        students = Student.objects.all()   # Retrieve all student instances from the database
        serializer = StudentSerializer(students, many=True)  # Create a serializer to convert the student instances to JSON data
        return JsonResponse(serializer.data, safe=False)
    
    
     # Define a method to handle POST requests to create a new student

    def post(self, request):
        students = Student.objects.all()   # Retrieve all student instances from the database
        serializer = StudentSerializer(students, many=True)  # Create a serializer to convert the student instances to JSON data
        return JsonResponse(serializer.data, safe=False)
        # return Response(status=200)
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StudentDetail(APIView):
    """
    Retrieve, update or delete a student instance.
    """
    
    def get_object(self, pk):
        try:
            return Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return None

    def get(self, request, pk):
        student = self.get_object(pk)
        if student is None:
            return JsonResponse({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = StudentSerializer(student)
        return JsonResponse(serializer.data)

    def put(self, request, pk):
        student = self.get_object(pk)
        if student is None:
            return JsonResponse({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        student = self.get_object(pk)
        if student is None:
            return JsonResponse({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        student.delete()
        return JsonResponse({'message': 'Student deleted successfully'}, status=status.HTTP_204_NO_CONTENT)