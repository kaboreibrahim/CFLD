import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils import timezone

from Apps.families.models import Family
from Apps.person.models import Person
from Apps.villages.models import Village

