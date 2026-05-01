from django.core.management.base import BaseCommand
from portal.models import Category, Skill

class Command(BaseCommand):
    help = 'Seeds the database with initial categories and skills'

    def handle(self, *args, **kwargs):
        categories = ['IT & Software', 'Marketing', 'Finance', 'Design', 'Sales', 'Customer Support']
        skills = ['Python', 'Django', 'MySQL', 'JavaScript', 'React', 'Bootstrap', 'HTML', 'CSS', 'AWS', 'Git', 'Java', 'PHP', 'Social Media', 'SEO', 'Data Analysis']

        for cat_name in categories:
            Category.objects.get_or_create(name=cat_name)
        
        for skill_name in skills:
            Skill.objects.get_or_create(name=skill_name)

        self.stdout.write(self.style.SUCCESS('Successfully seeded categories and skills'))
