import os
import json
from datetime import datetime
from celery import shared_task
from .models import Author, Book, BorrowRecord

@shared_task
def generate_report_task():
    # Calculate totals
    total_authors = Author.objects.count()
    total_books = Book.objects.count()
    total_borrowed_books = BorrowRecord.objects.filter(return_date__isnull=True).count()

    # Prepare report data
    report_data = {
        "total_authors": total_authors,
        "total_books": total_books,
        "total_borrowed_books": total_borrowed_books,
        "generated_at": datetime.now().isoformat(),
    }

    # Save report to JSON file
    reports_dir = os.path.join(os.getcwd(), "reports")
    os.makedirs(reports_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(reports_dir, f"report_{timestamp}.json")

    with open(report_file, 'w') as file:
        json.dump(report_data, file, indent=4)

    return report_file
