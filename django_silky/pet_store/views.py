from django.shortcuts import render_to_response


def pets(request):
    return render_to_response('pet_store/pets.html')