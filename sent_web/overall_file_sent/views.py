from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
import re
# Create your views here.
from .overall_sent import OverallSent,SentimentClassifier,CommentsSummary
from .models import OverallSentiment
from .forms import OverallSentimentForm
from django.contrib import messages

sent_class = SentimentClassifier()
comments_summarizer = CommentsSummary(llm_model_name='llama3.2:3b')

def file_overall(request):
    if not request.user.is_authenticated:
        return redirect('login_create_acc')

    form = None
    if request.method == 'POST':
        try:
            instance = OverallSentiment.objects.get(name_id = request.POST['name_id'],autor_id = request.user)
            form = OverallSentimentForm(request.POST,request.FILES,instance=instance)
        except OverallSentiment.DoesNotExist:
            form = OverallSentimentForm(request.POST,request.FILES)

        if form.is_valid():
            name = form.cleaned_data['name_id']
            try:
                file = form.cleaned_data['input_file'] #request.FILES['file_classification']
                comments = file.read().decode('utf-8')
                separator = '<SEP>'
                overall_sent = sent_class.process_comments(comments,separator=separator)
                overall_description = comments_summarizer.get_summary(comments=comments,
                                                                      separator=separator,
                                                                      complexity='one short paragraph')
                if len(overall_description) > 10000: overall_description = overall_description[:10000]
                analysis = form.save(commit=False) #temporarily saving the form
                analysis.autor_id = request.user
                analysis.pos_count = overall_sent.sent_count['Positive']
                analysis.neg_count = overall_sent.sent_count['Negative']
                analysis.neutral_count = overall_sent.sent_count['Neutral']
                analysis.overall_description = overall_description
                analysis.save()

                context = {
                    'idendity_name':name,
                    'res_stats':overall_sent.sent_count,
                    'individual_res':overall_sent.sentences,
                    'overall_description':overall_description,
                    'form':form
                }

                return render(request,'file_sent_overall.html',context)
            except Exception as e:
                return HttpResponse(e)
                #error_msgs.append('Invalid input file')
        else:
            messages.error(request, form.errors.as_text())
            #return HttpResponse(form.errors.as_text())
            
    

    return render(request,'file_sent_overall.html',{'form':OverallSentimentForm() if form is None else form})

from django.contrib import auth
from django.db.models import Q

def analysis_search(request):
    if 'search_text' in request.GET:
        search_text = request.GET['search_text']
        only_my_work = 'only_my_work' in request.GET
        analysis = []
        if auth.get_user(request).is_authenticated and only_my_work:
            analysis = OverallSentiment.objects.filter( Q(name_id__icontains=search_text), autor_id = request.user  )
        elif len(search_text) > 2:
            analysis = OverallSentiment.objects.filter( Q(name_id__icontains=search_text),is_public=True )

        if len(analysis) > 0:
            data_res = [ {'pk':res.pk,
                        'name_id':res.name_id,
                        'autor_id':res.autor_id,
                        'updated_at':res.updated_at,
                        'pos_avg': res.pos_count / (res.pos_count+res.neg_count+res.neutral_count) * 100 } for res in analysis ]
            context = { 'search_result':data_res }
            return render(request,'analysis_search.html',context)      

    return render(request,'analysis_search.html')

def analysis_viwer(request,pk):
    res = get_object_or_404(OverallSentiment,pk=pk)
    context = {'res':res}
    return render(request,'analysis_viwer.html',context)

def delete_analysis(request,pk):
    res = get_object_or_404(OverallSentiment,pk=pk)
    res.delete()
    return redirect('home')

def update_analysis(request,pk):
    if request.method == 'POST':
        print(request.POST)
        name_id = request.POST['name']
        if OverallSentimentForm.is_name_id_valid(name_id):
            res = get_object_or_404(OverallSentiment,pk=pk,autor_id=request.user)
            res.is_public = request.POST['is_public'] == 'true' #using hidden checkbox is used as true or false string
            res.name_id = name_id
            res.save()
    
    return redirect('home')