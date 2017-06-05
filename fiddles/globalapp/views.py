from django.shortcuts import render, redirect
import requests

def pass_through(request):
    print(self.request.path)
    return redirect(self.request.path)
