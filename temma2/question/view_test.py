from rest_framework.views import APIView
from .helper_functions import email_by_template
import json
from rest_framework.response import Response
from django.core.mail import EmailMessage
import pandas as pd
from .models import Sector, JobTitle
from rest_framework.permissions import(
    IsAuthenticated,
    IsAdminUser,
    AllowAny
    )
class StudentAdd(APIView):

    def get(self, request):
        jobs = {
            "Humanities": [
            "Historian",
            "Philosopher",
            "Writer/Author",
            "Linguist",
            "Art Curator",
            "Musician/Composer",
            "Cultural Anthropologist",
            "Archaeologist",
            "Art Critic",
            "Literary Critic",
            "Archivist",
            "Theologian",
            "Museum Director",
            "Poet",
            "Translator",
            "Drama Teacher",
            "Costume Designer",
            "Film Director",
            "Screenwriter",
            "Editor"
            ],
            "Social Sciences": [
            "Sociologist",
            "Psychologist",
            "Economist",
            "Political Scientist",
            "Social Worker",
            "Anthropologist",
            "Criminologist",
            "Geographer",
            "Urban Planner",
            "Demographer",
            "Market Research Analyst",
            "Public Policy Analyst",
            "International Relations Specialist",
            "Lawyer",
            "Mediator",
            "Marriage and Family Therapist",
            "Public Health Administrator",
            "Community Service Manager",
            "Paralegal",
            "Social and Human Service Assistant"
            ],
            "Biological Sciences": [
            "Biologist",
            "Microbiologist",
            "Geneticist",
            "Marine Biologist",
            "Zoologist",
            "Botanist",
            "Ecologist",
            "Wildlife Biologist",
            "Environmental Scientist",
            "Entomologist",
            "Immunologist",
            "Biotechnologist",
            "Aquatic Scientist",
            "Conservation Biologist",
            "Paleontologist",
            "Neuroscientist"
            ],
            "Physical Sciences": [
            "Physicist",
            "Chemist",
            "Geologist",
            "Meteorologist",
            "Astronomer",
            "Oceanographer",
            "Seismologist",
            "Astrophysicist",
            "Hydrologist",
            "Geophysicist",
            "Materials Scientist",
            "Nuclear Scientist",
            "Climatologist",
            "Volcanologist",
            "Environmental Chemist"
            ],
            "Engineering and Technology": [
            "Civil Engineer",
            "Mechanical Engineer",
            "Electrical Engineer",
            "Software Engineer",
            "Biomedical Engineer",
            "Environmental Engineer",
            "Chemical Engineer",
            "Aerospace Engineer",
            "Industrial Engineer",
            "Nuclear Engineer",
            "Computer Hardware Engineer",
            "Systems Engineer",
            "Robotics Engineer",
            "Automotive Engineer",
            "Telecommunications Engineer",
            "Mining Engineer",
            "Petroleum Engineer"
            ],
            "Medical and Health Sciences": [
            "Medical Doctor",
            "Nurse",
            "Pharmacist",
            "Dentist",
            "Veterinarian",
            "Optometrist",
            "Physiotherapist",
            "Radiologist",
            "Chiropractor",
            "Anesthesiologist",
            "Surgeon",
            "Clinical Researcher",
            "Public Health Specialist",
            "Epidemiologist",
            "Occupational Therapist",
            "Dietitian/Nutritionist",
            "Podiatrist",
            "Speech Therapist",
            "Medical Lab Technician",
            "Psychiatrist"
            ],
            "Architecture and Design": [
            "Architect",
            "Interior Designer",
            "Landscape Architect",
            "Urban Planner",
            "Structural Engineer",
            "Building Surveyor",
            "Lighting Designer",
            "Industrial Designer",
            "Graphic Designer",
            "Textile Designer",
            "Fashion Designer",
            "Product Designer",
            "Furniture Designer",
            "Set Designer",
            "Visual Merchandiser"
            ],
            "Information Technology": [
            "Software Developer",
            "Web Developer",
            "Data Scientist",
            "Database Administrator",
            "Cybersecurity Analyst",
            "IT Manager",
            "Network Administrator",
            "Cloud Engineer",
            "Artificial Intelligence Engineer",
            "DevOps Engineer",
            "Mobile App Developer",
            "Game Developer",
            "Systems Analyst",
            "Business Intelligence Analyst",
            "Technical Support Specialist",
            "UI/UX Designer",
            "Blockchain Developer"
            ],
            "Mathematics and Statistics": [
            "Mathematician",
            "Statistician",
            "Data Analyst",
            "Actuary",
            "Operations Research Analyst",
            "Cryptographer",
            "Risk Analyst",
            "Quantitative Analyst",
            "Logician",
            "Mathematical Modeler",
            "Econometrician",
            "Biostatistician",
            "Demographer",
            "Operations Manager",
            "Market Analyst"
            ],
            "Computer Sciences and Theoretical Fields": [
            "Computer Scientist",
            "Theoretical Physicist",
            "Algorithm Developer",
            "Machine Learning Engineer",
            "Natural Language Processing Specialist",
            "Quantum Computing Researcher",
            "Artificial Intelligence Researcher",
            "Software Architect",
            "Systems Programmer",
            "Robotics Researcher",
            "Distributed Systems Engineer",
            "Database Theorist",
            "Information Retrieval Specialist",
            "Cybernetics Researcher"
            ]
        }


        for sector in jobs.keys():
            
            # path = f"/home/demotemma2/temma_pytanywhere/temma/question/datas/job_titles/{sector}.json"
            # with open(path, 'r') as file:
            #     data = json.load(file)
            # print(data)
            # data_unique = [dict(t) for t in {tuple(d.items()) for d in data}]
            # with open('./question/datas/job_titles/data_unique.json', 'w') as file:
            #     json.dump(data_unique, file, indent=4)
            sec = Sector.objects.get(sector=sector)
            # JobTitle.objects.filter(sector=sec).delete()
            for job in jobs[sector]:
                
                JobTitle.objects.create(sector=sec, job_title = job)



        # pass
            # email_by_template(subject="BAAANG we found a mentor for you!",
            #                 ctx={'mentor_name':mentor_instance.name, 'mentor_email':mentor_instance.email, "mentor_study":study,
            #                     'mentee_unsubscribe':user_instance.id},
            #                 template_path='mentor-details-for-student.html', to=[user_instance.email])

            # email_by_template(subject="",
            #                 ctx={'mentor_name':mentor_instance.name, 'email_scholier':user_instance.email,
            #                      'mentor_unsubscribe':mentor_instance.id},
            #                 template_path='mentee_data_for_mentor.html', to=[mentor_instance.email])
        # email_by_template()
        # df = pd.read_excel("./question/Mentoren voor Mentor Match  (2).xlsx")
        # for i in range(34, 75):
        #     try:
        #         name = df['Name'][i]
        #         email = df['email'][i]
        #         email_by_template(subject="Surprise! Verkeerde afzender, juiste boodschap 😄",ctx={'name':name},
        #                             template_path='mentor-register.html', to=[email])
        #     except:
        #         pass


        # Attach the HTML content as alternative content
        # msg.attach_alternative(html_content, "text/html")

        # # Send the email
        # msg.send()

        # send_email_with_HTML_test(subject="Surprise! Verkeerde afzender, juiste boodschap 😄", 
        #                           html_content='mentor-register.html', text_content=text, to=["fayyoz1@mail.ru"])
        return Response({"message":"Done!"}, status=200)

        # path=""
        # with open(path, 'r') as file:
        #     data = json.load(file)
        # for d in data:
        #     pass
            # sector=MentorSector.objects.get(sector=d['Sector'])
            # name=d['Name']
            # email=d['E-mail adres']
            # Student.objects.create(name=name, sector=sector, email=email)
from .views import generate_token, config, MentorForScholier, MentorMatchScholier, email_sender_for_admin

class RerunSystem(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
        # pass
        mentee_objects=MentorMatchScholier.objects.filter(is_replied=False)

        for obj in mentee_objects:
            mentor_obj = MentorForScholier.objects.filter(
                                study__name=obj.study.name,
                                university__name=obj.university.name
                            ).first()

            if not mentor_obj:
                email_sender_for_admin(title="we still deon't have a mentor!, after rerunning the system", body=f"""
                        please add more mentors for scholier and the study is --> {obj.study}!,
                        University is --> {obj.university}!,
                    """, emails=["fayyoz1@mail.ru", "hiraanwar1998@gmail.com", "EvaSofia_@live.nl"])
                continue
            token = generate_token(user_id=obj.id, student_id=mentor_obj.id, user_type='scholier')

            email_by_template(subject="Klik op de link om een mentor te worden voor een scholier",
                            ctx={'mentor_name':mentor_obj.name,'mentor_unsubscribe':mentor_obj.id, 'token':token}, #{str(one_time_link)+str(token)}
                            template_path=config('MENTOR_CLICK_TOKEN'), to=[mentor_obj.email])
            print("token email is sent for admin!")
            print(f"Email is sent for {mentor_obj.email}")

        return Response({"message":"Done!"}, status=200)
    
from users.models import User
from users.utils import username_generator

class RerunMentor(APIView):
    def get(self, request):
        mentors = MentorForScholier.objects.all()
        for mentor in mentors:
            email = mentor.email
            name = mentor.name
            if not mentor.user:
                try:
                    user = User.objects.get(email=email)
                except:
                    username = username_generator(name=name)
                    user = User.objects.create(username = username, email=email)
                    user.set_password(username)
                    user.save()
                mentor.user = user
                mentor.save()

        return Response({"detail":"got it"}, status=200)