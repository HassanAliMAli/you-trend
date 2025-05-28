"""
Report Generator Module for YouTrend

This module generates reports in various formats (TXT, CSV, XLSX, PDF)
containing YouTube trend analysis data and insights.
"""

import io
import csv
# import json # Unused
from typing import Dict, List, Any, Union, BinaryIO
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

def generate_txt_report(data: Dict[str, Any], report_type: str = 'trend') -> str:
    """
    Generate a plain text report from YouTube trend data.
    The 'data' structure is expected to align with outputs from analyze_video_trends for 'trend' type,
    and compare_niches for 'compare' type.
    """
    output = []
    output.append("YOUTREND ANALYSIS REPORT")
    output.append(f"Report Type: {report_type.capitalize()}")
    output.append("=" * 70)
    output.append("")
    
    if report_type == 'trend':
        output.append(f"Total Videos Analyzed: {data.get('total_videos_analyzed', 0)}")
        output.append(f"Average Views: {data.get('average_views', 0):,.0f}")
        output.append(f"Average Engagement Rate: {data.get('average_engagement_rate', 0):.2%}")
        output.append("")

        if 'top_videos' in data and data['top_videos']:
            output.append("TOP VIDEOS")
            output.append("-" * 70)
            for i, video in enumerate(data['top_videos'], 1):
                output.append(f"{i}. Title: {video.get('title', 'N/A')}")
                output.append(f"   Channel: {video.get('channel_title', 'N/A')}")
                output.append(f"   Views: {video.get('views', 0):,}")
                output.append(f"   Likes: {video.get('likes', 0):,}")
                output.append(f"   Comments: {video.get('comments', 0):,}")
                output.append(f"   Published: {video.get('published_at', 'N/A')}")
                output.append(f"   Score: {video.get('score', 0.0):.4f}")
                output.append(f"   URL: https://www.youtube.com/watch?v={video.get('id', '')}")
                output.append("")
        
        # Note: Channel list is not part of 'analyze_video_trends' output directly.
        # If separate channel analysis data is provided, it would need to be handled.

        if 'trending_topics' in data and data['trending_topics']:
            output.append("TRENDING TOPICS/FORMATS")
            output.append("-" * 70)
            for i, topic in enumerate(data['trending_topics'], 1):
                output.append(f"{i}. Topic: {topic.get('name', 'N/A')}")
                output.append(f"   Video Count: {topic.get('video_count', 0)}")
                output.append(f"   Avg Views/Video: {topic.get('avg_views_per_video', 0):,.0f}")
                output.append(f"   Score (Composite): {topic.get('composite_score', 0.0):.2f}")
                output.append("")

        if 'video_ideas' in data and data['video_ideas']:
            output.append("VIDEO IDEAS & INSIGHTS")
            output.append("-" * 70)
            for i, idea in enumerate(data['video_ideas'], 1):
                output.append(f"{i}. Idea: {idea.get('title', 'N/A')}")
                output.append(f"   Description: {idea.get('description', 'N/A')}")
                output.append(f"   Topic: {idea.get('topic', 'N/A')}")
                output.append(f"   Est. View Potential: {idea.get('estimated_view_potential', 'N/A')}")
                output.append(f"   Est. Competition: {idea.get('estimated_competition', 'N/A')}")
                output.append("")
    
    elif report_type == 'compare':
        # Data for 'compare' is expected to be Dict[niche_name, niche_analysis_data]
        # niche_analysis_data is similar to 'trend' report data for a single niche
        output.append("NICHE COMPARISON REPORT")
        output.append("-" * 70)
        for niche_name, niche_data in data.items():
            output.append("")
            output.append(f"NICHE: {niche_name.upper()}")
            output.append("~" * (len(niche_name) + 8))
            output.append(f"  Total Videos in Selection: {niche_data.get('total_videos_in_selection', 0)}")
            output.append(f"  Average Views: {niche_data.get('average_views', 0):,.0f}")
            output.append(f"  Average Engagement Rate: {niche_data.get('average_engagement_rate', 0):.2%}")
            output.append("")

            if 'top_videos' in niche_data and niche_data['top_videos']:
                output.append("  TOP VIDEOS IN NICHE:")
                for i, video in enumerate(niche_data['top_videos'][:3], 1): # Show top 3 for brevity
                    output.append(f"    {i}. Title: {video.get('title', 'N/A')} (Views: {video.get('views', 0):,}, Score: {video.get('score', 0.0):.4f})")
                output.append("")
            
            if 'top_channels_in_niche' in niche_data and niche_data['top_channels_in_niche']:
                output.append("  TOP CHANNELS PERFORMING IN THIS NICHE (based on provided videos):")
                for i, channel in enumerate(niche_data['top_channels_in_niche'][:3],1):
                     output.append(f"    {i}. Channel: {channel.get('title', 'N/A')} (Videos in selection: {channel.get('niche_video_count')}, Total views in selection: {channel.get('niche_total_views'):,})")
                output.append("")

            if 'trending_topics' in niche_data and niche_data['trending_topics']:
                output.append("  TRENDING TOPICS/FORMATS IN NICHE:")
                for i, topic in enumerate(niche_data['trending_topics'][:3], 1): # Show top 3
                    output.append(f"    {i}. Topic: {topic.get('name', 'N/A')} (Video Count: {topic.get('video_count',0)}, Avg Views: {topic.get('avg_views_per_video', 0):,.0f})")
                output.append("")
            output.append("-" * 70)

    output.append("")
    output.append("=" * 70)
    output.append("Generated by YouTrend - YouTube Trend Analysis Tool")
    
    return "\n".join(output)

def generate_csv_report(data: Dict[str, Any], report_type: str = 'trend') -> str:
    """
    Generate a CSV report from YouTube trend data.
    Adapts to the new data structures.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    if report_type == 'trend':
        writer.writerow(["TREND ANALYSIS REPORT"])
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Videos Analyzed", data.get('total_videos_analyzed', 0)])
        writer.writerow(["Average Views", f"{data.get('average_views', 0):.0f}"])
        writer.writerow(["Average Engagement Rate", f"{data.get('average_engagement_rate', 0):.4f}"])
        writer.writerow([])

        if 'top_videos' in data and data['top_videos']:
            writer.writerow(["TOP VIDEOS"])
            writer.writerow(["Rank", "Title", "Channel", "Views", "Likes", "Comments", "Published At", "Score", "URL"])
            for i, video in enumerate(data['top_videos'], 1):
                writer.writerow([
                    i,
                    video.get('title', 'N/A'),
                    video.get('channel_title', 'N/A'),
                    video.get('views', 0),
                    video.get('likes', 0),
                    video.get('comments', 0),
                    video.get('published_at', 'N/A'),
                    f"{video.get('score', 0.0):.4f}",
                    f"https://www.youtube.com/watch?v={video.get('id', '')}"
                ])
            writer.writerow([])
        
        if 'trending_topics' in data and data['trending_topics']:
            writer.writerow(["TRENDING TOPICS/FORMATS"])
            writer.writerow(["Rank", "Topic Name", "Video Count", "Aggregated Views", "Avg Views/Video", "Avg Engagement Score/Video", "Composite Score"])
            for i, topic in enumerate(data['trending_topics'], 1):
                writer.writerow([
                    i,
                    topic.get('name', 'N/A'),
                    topic.get('video_count', 0),
                    topic.get('aggregated_views', 0),
                    f"{topic.get('avg_views_per_video', 0):.0f}",
                    f"{topic.get('avg_engagement_score_per_video', 0.0):.2f}",
                    f"{topic.get('composite_score', 0.0):.2f}"
                ])
            writer.writerow([])

        if 'video_ideas' in data and data['video_ideas']:
            writer.writerow(["VIDEO IDEAS & INSIGHTS"])
            writer.writerow(["Rank", "Idea Title", "Description", "Associated Topic", "Est. View Potential", "Est. Competition"])
            for i, idea in enumerate(data['video_ideas'], 1):
                writer.writerow([
                    i,
                    idea.get('title', 'N/A'),
                    idea.get('description', 'N/A'),
                    idea.get('topic', 'N/A'),
                    idea.get('estimated_view_potential', 'N/A'),
                    idea.get('estimated_competition', 'N/A')
                ])
            writer.writerow([])

    elif report_type == 'compare':
        writer.writerow(["NICHE COMPARISON REPORT"])
        writer.writerow([])

        for niche_name, niche_data in data.items():
            writer.writerow([f"NICHE: {niche_name.upper()}"])
            writer.writerow(["Metric", "Value"])
            writer.writerow(["Total Videos in Selection", niche_data.get('total_videos_in_selection', 0)])
            writer.writerow(["Average Views", f"{niche_data.get('average_views', 0):.0f}"])
            writer.writerow(["Average Engagement Rate", f"{niche_data.get('average_engagement_rate', 0):.4f}"])
            writer.writerow([])

            if 'top_videos' in niche_data and niche_data['top_videos']:
                writer.writerow(["Top Videos in Niche (Max 5)"])
                writer.writerow(["Rank", "Title", "Views", "Score"])
                for i, video in enumerate(niche_data['top_videos'][:5], 1):
                    writer.writerow([
                        i,
                        video.get('title', 'N/A'),
                        video.get('views', 0),
                        f"{video.get('score', 0.0):.4f}"
                    ])
                writer.writerow([])

            if 'top_channels_in_niche' in niche_data and niche_data['top_channels_in_niche']:
                writer.writerow(["Top Channels in Niche (Max 5, based on videos in selection)"])
                writer.writerow(["Rank","Channel Title", "Videos in Selection", "Total Views in Selection"])
                for i, channel in enumerate(niche_data['top_channels_in_niche'][:5],1):
                    writer.writerow([
                        i,
                        channel.get('title','N/A'),
                        channel.get('niche_video_count'),
                        channel.get('niche_total_views')
                    ])
                writer.writerow([])

            if 'trending_topics' in niche_data and niche_data['trending_topics']:
                writer.writerow(["Trending Topics/Formats in Niche (Max 5)"])
                writer.writerow(["Rank", "Topic Name", "Video Count", "Avg Views/Video"])
                for i, topic in enumerate(niche_data['trending_topics'][:5], 1):
                    writer.writerow([
                        i,
                        topic.get('name', 'N/A'),
                        topic.get('video_count', 0),
                        f"{topic.get('avg_views_per_video', 0):.0f}"
                    ])
                writer.writerow([])
            writer.writerow(["-"*5]) # Separator for niches
            writer.writerow([])
            
    return output.getvalue()

def generate_excel_report(data: Dict[str, Any], report_type: str = 'trend', include_charts: bool = True) -> BinaryIO:
    """
    Generate an Excel report from YouTube trend data.
    Adapts to the new data structures from data_processor.
    """
    output = io.BytesIO()
    workbook = None # Define workbook here to ensure it's accessible in finally block if needed

    try:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book
            header_format = workbook.add_format({'bold': True, 'bg_color': '#D9E1F2', 'border': 1})
            cell_format = workbook.add_format({'border': 1})

            if report_type == 'trend':
                # Summary Sheet for Trend Report
                summary_data = {
                    "Metric": ["Total Videos Analyzed", "Average Views", "Average Engagement Rate"],
                    "Value": [
                        data.get('total_videos_analyzed', 0),
                        f"{data.get('average_views', 0):.0f}",
                        f"{data.get('average_engagement_rate', 0):.4f}"
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Trend Summary', index=False, header=False, startrow=1)
                worksheet = writer.sheets['Trend Summary']
                worksheet.write_string(0, 0, "Trend Analysis Summary", header_format)
                for col_num, value in enumerate(summary_df.columns.values):
                     worksheet.write(1, col_num, value, header_format)
                for row_num in range(len(summary_df)):
                    for col_num in range(len(summary_df.columns)):
                        worksheet.write(row_num + 2, col_num, summary_df.iloc[row_num, col_num], cell_format)
                worksheet.set_column(0, 1, 30) # Adjust column width

                # Top Videos Sheet
                if 'top_videos' in data and data['top_videos']:
                    videos_df_data = []
                    for v in data['top_videos']:
                        videos_df_data.append({
                            "Title": v.get('title', 'N/A'),
                            "Channel": v.get('channel_title', 'N/A'),
                            "Views": v.get('views', 0),
                            "Likes": v.get('likes', 0),
                            "Comments": v.get('comments', 0),
                            "Published": v.get('published_at', 'N/A'),
                            "Score": f"{v.get('score', 0.0):.4f}",
                            "URL": f"https://www.youtube.com/watch?v={v.get('id', '')}"
                        })
                    videos_df = pd.DataFrame(videos_df_data)
                    videos_df.to_excel(writer, sheet_name='Top Videos', index=False)
                    _apply_table_style(writer.sheets['Top Videos'], videos_df, header_format, cell_format)
                    if include_charts and not videos_df.empty:
                        _add_charts_to_excel(workbook, writer.sheets['Top Videos'], 'Top Videos by Views', videos_df, 'Title', 'Views', 'A10')

                # Trending Topics Sheet
                if 'trending_topics' in data and data['trending_topics']:
                    topics_df_data = []
                    for t in data['trending_topics']:
                        topics_df_data.append({
                            "Topic Name": t.get('name', 'N/A'),
                            "Video Count": t.get('video_count', 0),
                            "Agg. Views": t.get('aggregated_views', 0),
                            "Avg Views/Video": f"{t.get('avg_views_per_video', 0):.0f}",
                            "Avg Eng. Score/Video": f"{t.get('avg_engagement_score_per_video', 0.0):.2f}",
                            "Composite Score": f"{t.get('composite_score', 0.0):.2f}"
                        })
                    topics_df = pd.DataFrame(topics_df_data)
                    topics_df.to_excel(writer, sheet_name='Trending Topics', index=False)
                    _apply_table_style(writer.sheets['Trending Topics'], topics_df, header_format, cell_format)
                    if include_charts and not topics_df.empty:
                         _add_charts_to_excel(workbook, writer.sheets['Trending Topics'], 'Top Topics by Avg Views', topics_df, 'Topic Name', 'Avg Views/Video', 'A12', value_is_str_num=True)

                # Video Ideas Sheet
                if 'video_ideas' in data and data['video_ideas']:
                    ideas_df_data = []
                    for idea in data['video_ideas']:
                        ideas_df_data.append({
                            "Idea Title": idea.get('title', 'N/A'),
                            "Description": idea.get('description', 'N/A'),
                            "Topic": idea.get('topic', 'N/A'),
                            "Est. View Potential": idea.get('estimated_view_potential', 'N/A'),
                            "Est. Competition": idea.get('estimated_competition', 'N/A')
                        })
                    ideas_df = pd.DataFrame(ideas_df_data)
                    ideas_df.to_excel(writer, sheet_name='Video Ideas', index=False)
                    _apply_table_style(writer.sheets['Video Ideas'], ideas_df, header_format, cell_format)

            elif report_type == 'compare':
                # Create a summary sheet for comparison
                compare_summary_data = []
                for niche_name, niche_data in data.items():
                    compare_summary_data.append({
                        "Niche": niche_name,
                        "Total Videos Analyzed": niche_data.get('total_videos_in_selection', 0),
                        "Average Views": niche_data.get('average_views', 0),
                        "Average Engagement Rate": niche_data.get('average_engagement_rate', 0)
                    })
                compare_summary_df = pd.DataFrame(compare_summary_data)
                compare_summary_df.to_excel(writer, sheet_name='Niche Comparison Summary', index=False)
                _apply_table_style(writer.sheets['Niche Comparison Summary'], compare_summary_df, header_format, cell_format)
                if include_charts and not compare_summary_df.empty:
                    _add_charts_to_excel(workbook, writer.sheets['Niche Comparison Summary'], 'Niche Avg Views', compare_summary_df, 'Niche', 'Average Views', 'F2')
                    _add_charts_to_excel(workbook, writer.sheets['Niche Comparison Summary'], 'Niche Avg Engagement', compare_summary_df, 'Niche', 'Average Engagement Rate', 'F20')

                # Create individual sheets for each niche in the comparison
                for niche_name, niche_data in data.items():
                    sheet_name = f"Niche - {niche_name[:20]}" # Truncate sheet name if too long
                    
                    # Videos in this niche
                    if 'top_videos' in niche_data and niche_data['top_videos']:
                        videos_df_data = []
                        for v in niche_data['top_videos']:
                            videos_df_data.append({
                                "Title": v.get('title', 'N/A'), "Views": v.get('views',0), "Score": f"{v.get('score',0.0):.4f}"
                            })
                        niche_videos_df = pd.DataFrame(videos_df_data)
                        niche_videos_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=0)
                        worksheet = writer.sheets[sheet_name]
                        _apply_table_style(worksheet, niche_videos_df, header_format, cell_format, header_text=f"{niche_name} - Top Videos")
                        current_row = len(niche_videos_df) + 3
                    else:
                        worksheet = workbook.add_worksheet(sheet_name)
                        worksheet.write_string(0,0, f"{niche_name} - No Top Video Data", header_format)
                        current_row = 2
                    
                    # Topics in this niche
                    if 'trending_topics' in niche_data and niche_data['trending_topics']:
                        topics_df_data = []
                        for t in niche_data['trending_topics']:
                            topics_df_data.append({
                                "Topic Name": t.get('name', 'N/A'), "Video Count": t.get('video_count',0), "Avg Views/Video": f"{t.get('avg_views_per_video', 0):.0f}"
                            })
                        niche_topics_df = pd.DataFrame(topics_df_data)
                        niche_topics_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=current_row)
                        _apply_table_style(worksheet, niche_topics_df, header_format, cell_format, start_row_offset=current_row, header_text=f"{niche_name} - Trending Topics")
                        # current_row += len(niche_topics_df) + 3 # Update current_row if more sections added

                    # Could also add top channels in niche if that data is present and desired
    except Exception as e:
        # Consider logging the error or raising a specific report generation error
        # For now, if excel generation fails, it might return an empty/corrupt BytesIO
        # The caller in api/reports.py handles general exceptions during generate_report_task
        print(f"Error during Excel generation: {e}") # Basic print for now
        # Ensure output is a valid BytesIO object even on error, or handle upstream
        if workbook is None and output.tell() == 0: # No workbook created and output is empty
             # Create a minimal valid xlsx if absolutely necessary, or rely on upstream error handling
             pass # Let the possibly empty BytesIO be returned

    output.seek(0)
    return output

def _apply_table_style(worksheet, df, header_format, cell_format, start_row_offset=0, header_text=None):
    """Helper to apply formatting to an Excel sheet table."""
    if header_text:
        worksheet.write_string(start_row_offset, 0, header_text, header_format)
        start_row_offset +=1

    max_col = len(df.columns) -1 
    max_row = len(df) + start_row_offset

    for col_num, value in enumerate(df.columns.values):
        worksheet.write(start_row_offset, col_num, value, header_format)
    
    for row_idx in range(len(df)):
        for col_idx in range(len(df.columns)):
            worksheet.write(row_idx + start_row_offset + 1, col_idx, df.iloc[row_idx, col_idx], cell_format)
    
    # Auto-adjust column widths (simple approach)
    for i, col in enumerate(df.columns):
        column_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
        worksheet.set_column(i, i, min(column_len, 50)) # Cap width at 50


def _add_charts_to_excel(workbook, worksheet, chart_title: str, df: pd.DataFrame, category_col: str, value_col: str, position: str, value_is_str_num: bool = False):
    """Helper function to add a bar chart to an Excel sheet."""
    if df.empty or category_col not in df.columns or value_col not in df.columns:
        return
    
    chart = workbook.add_chart({'type': 'bar'})
    chart.set_title({'name': chart_title})
    chart.set_legend({'position': 'none'})

    # Prepare data for chart, converting string numbers if necessary
    categories = df[category_col].tolist()
    if value_is_str_num:
        try:
            # Attempt to convert string numbers like "1,234" or "1234.00" to float
            values = [float(str(v).replace(',','')) for v in df[value_col].tolist()]
        except ValueError:
            return # Cannot create chart if values are not numeric
    else:
        values = df[value_col].tolist()
    
    # Find the sheet name for referencing
    sheet_name = ''
    for ws_name, ws_obj in workbook.sheetnames.items():
        if ws_obj == worksheet:
            sheet_name = ws_name
            break
    if not sheet_name: return # Should not happen

    # Write data to temporary hidden columns for chart source if not directly referencable
    # This is a robust way if direct cell refs are tricky.
    # For simplicity, assume data is already in cells from df.to_excel and try to reference that.
    # Find column index for category and value
    cat_col_idx = df.columns.get_loc(category_col) + 1 # 1-indexed for Excel
    val_col_idx = df.columns.get_loc(value_col) + 1 # 1-indexed for Excel
    header_offset = 1 # Assuming 1 header row from df.to_excel

    # Need to adjust if df.to_excel starts at a different row.
    # For now, assume df.to_excel writes headers at row 1, data starts at row 2.
    # The following is a simplified way to reference data. More robust would be to write to helper cells.
    chart.add_series({
        'name':       f"='{sheet_name}'!${chr(ord('A') + val_col_idx -1)}${header_offset}",
        'categories': f"='{sheet_name}'!${chr(ord('A') + cat_col_idx -1)}${header_offset+1}:${chr(ord('A') + cat_col_idx-1)}${header_offset+len(df)}",
        'values':     f"='{sheet_name}'!${chr(ord('A') + val_col_idx -1)}${header_offset+1}:${chr(ord('A') + val_col_idx-1)}${header_offset+len(df)}",
    })
    worksheet.insert_chart(position, chart)

def generate_pdf_report(data: Dict[str, Any], report_type: str = 'trend', include_charts: bool = True) -> BinaryIO:
    """
    Generate a PDF report from YouTube trend data, adapting to new data structures.
    Includes table generation and optional charts.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=inch/2, leftMargin=inch/2,
                            topMargin=inch/2, bottomMargin=inch/2)
    styles = getSampleStyleSheet()
    story: List[Any] = [] # Ensure story is explicitly typed for clarity

    # Title
    title_style = styles['h1']
    title_style.alignment = TA_CENTER
    story.append(Paragraph("YouTrend Analysis Report", title_style))
    story.append(Paragraph(f"Report Type: {report_type.capitalize()}", styles['h2']))
    story.append(Spacer(1, 0.2*inch))

    body_style = styles['Normal']
    table_header_style = ParagraphStyle('TableHeader', parent=styles['Normal'], fontName='Helvetica-Bold')

    if report_type == 'trend':
        # Trend Summary Info
        story.append(Paragraph(f"<b>Total Videos Analyzed:</b> {data.get('total_videos_analyzed', 0)}", body_style))
        story.append(Paragraph(f"<b>Average Views:</b> {data.get('average_views', 0):,.0f}", body_style))
        story.append(Paragraph(f"<b>Average Engagement Rate:</b> {data.get('average_engagement_rate', 0):.2%}", body_style))
        story.append(Spacer(1, 0.2*inch))

        # Top Videos Table
        if 'top_videos' in data and data['top_videos']:
            story.append(Paragraph("Top Videos", styles['h3']))
            videos_data_pdf = [[
                Paragraph("Title", table_header_style),
                Paragraph("Channel", table_header_style),
                Paragraph("Views", table_header_style),
                Paragraph("Score", table_header_style)
            ]]
            for v in data['top_videos'][:10]: # Limit for PDF page
                videos_data_pdf.append([
                    Paragraph(str(v.get('title', 'N/A'))[:50], body_style),
                    Paragraph(str(v.get('channel_title', 'N/A'))[:30], body_style),
                    Paragraph(f"{v.get('views', 0):,}", body_style),
                    Paragraph(f"{v.get('score', 0.0):.4f}", body_style)
                ])
            video_table = Table(videos_data_pdf, colWidths=[2.5*inch, 2*inch, 1.5*inch, 1*inch])
            video_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ]))
            story.append(video_table)
            story.append(Spacer(1, 0.1*inch))
            if include_charts and data['top_videos']:
                chart_img = _create_bar_chart_image(data['top_videos'][:10], 'title', 'views', 'Top 10 Videos by Views')
                if chart_img:
                    story.append(Image(chart_img, width=6*inch, height=3.5*inch)) # Adjusted height
                story.append(Spacer(1, 0.2*inch))

        # Trending Topics Table
        if 'trending_topics' in data and data['trending_topics']:
            story.append(Paragraph("Trending Topics/Formats", styles['h3']))
            topics_data_pdf = [[
                Paragraph("Topic", table_header_style),
                Paragraph("Video Count", table_header_style),
                Paragraph("Avg Views/Video", table_header_style),
                Paragraph("Score", table_header_style)
            ]]
            for t in data['trending_topics'][:10]:
                topics_data_pdf.append([
                    Paragraph(str(t.get('name', 'N/A'))[:50], body_style),
                    Paragraph(str(t.get('video_count', 0)), body_style),
                    Paragraph(f"{t.get('avg_views_per_video', 0):,.0f}", body_style),
                    Paragraph(f"{t.get('composite_score', 0.0):.2f}", body_style)
                ])
            topic_table = Table(topics_data_pdf, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
            topic_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey), ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 12), ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ]))
            story.append(topic_table)
            story.append(Spacer(1, 0.1*inch))
            if include_charts and data['trending_topics']:
                # Using 'avg_views_per_video' which is already numeric.
                chart_img = _create_bar_chart_image(data['trending_topics'][:10], 'name', 'avg_views_per_video', 'Avg Views per Video by Topic (Top 10)')
                if chart_img:
                    story.append(Image(chart_img, width=6*inch, height=3.5*inch)) # Adjusted height
                story.append(Spacer(1, 0.2*inch))

        # Video Ideas
        if 'video_ideas' in data and data['video_ideas']:
            story.append(Paragraph("Video Ideas & Insights", styles['h3']))
            for i, idea in enumerate(data['video_ideas'][:5], 1): # Limit for PDF
                story.append(Paragraph(f"<b>{i}. Idea:</b> {str(idea.get('title', 'N/A'))[:100]}", body_style))
                story.append(Paragraph(f"   <i>Description:</i> {str(idea.get('description', 'N/A'))[:250]}...", body_style))
                story.append(Paragraph(f"   <i>Topic:</i> {str(idea.get('topic', 'N/A'))}", body_style))
                story.append(Paragraph(f"   <i>Est. View Potential:</i> {str(idea.get('estimated_view_potential', 'N/A'))}", body_style))
                story.append(Paragraph(f"   <i>Est. Competition:</i> {str(idea.get('estimated_competition', 'N/A'))}", body_style))
                story.append(Spacer(1, 0.1*inch))

    elif report_type == 'compare':
        story.append(Paragraph("Niche Comparison Overview", styles['h2']))
        story.append(Spacer(1, 0.1*inch))

        summary_table_data = [[
            Paragraph("Niche", table_header_style),
            Paragraph("Avg Views", table_header_style),
            Paragraph("Avg Engagement %", table_header_style),
            Paragraph("Total Videos", table_header_style)
        ]]
        chart_summary_list = []
        for niche_name, niche_data in data.items():
            chart_summary_list.append({
                'niche_name': niche_name, # For chart categories
                'average_views': niche_data.get('average_views', 0)
            })
            summary_table_data.append([
                Paragraph(niche_name, body_style),
                Paragraph(f"{niche_data.get('average_views', 0):,.0f}", body_style),
                Paragraph(f"{niche_data.get('average_engagement_rate', 0):.2%}", body_style),
                Paragraph(str(niche_data.get('total_videos_in_selection', 0)), body_style)
            ])

        summary_col_widths = [2.5*inch, 1.5*inch, 1.5*inch, 2*inch]
        summary_table = Table(summary_table_data, colWidths=summary_col_widths)
        summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey), ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 12), ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.1*inch))

        if include_charts and chart_summary_list:
            chart_img = _create_bar_chart_image(chart_summary_list, 'niche_name', 'average_views', 'Average Views per Niche')
            if chart_img:
                story.append(Image(chart_img, width=6*inch, height=3.5*inch))
            story.append(Spacer(1, 0.2*inch))
        
        story.append(PageBreak())

        for niche_name, niche_data in data.items():
            story.append(Paragraph(f"Details for Niche: {niche_name}", styles['h3']))
            story.append(Paragraph(f"<b>Total Videos in Selection:</b> {niche_data.get('total_videos_in_selection', 0)}", body_style))
            story.append(Paragraph(f"<b>Average Views:</b> {niche_data.get('average_views', 0):,.0f}", body_style))
            story.append(Paragraph(f"<b>Average Engagement Rate:</b> {niche_data.get('average_engagement_rate', 0):.2%}", body_style))
            story.append(Spacer(1, 0.1*inch))

            if 'top_videos' in niche_data and niche_data['top_videos']:
                story.append(Paragraph("Top Videos in Niche (Max 5):", styles['Normal']))
                niche_videos_pdf = [[Paragraph("Title", table_header_style), Paragraph("Views", table_header_style), Paragraph("Score", table_header_style)]]
                for v in niche_data['top_videos'][:5]:
                    niche_videos_pdf.append([
                        Paragraph(str(v.get('title', 'N/A'))[:60], body_style),
                        Paragraph(f"{v.get('views', 0):,}", body_style),
                        Paragraph(f"{v.get('score', 0.0):.4f}", body_style)
                    ])
                niche_video_table = Table(niche_videos_pdf, colWidths=[4*inch, 1.5*inch, 1.5*inch])
                niche_video_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.lightgrey), ('GRID', (0,0), (-1,-1), 1, colors.black)]))
                story.append(niche_video_table)
                story.append(Spacer(1, 0.2*inch))

            if 'top_channels_in_niche' in niche_data and niche_data['top_channels_in_niche']:
                story.append(Paragraph("Top Channels in Niche (Max 3, based on videos):", styles['Normal']))
                niche_channels_pdf = [[Paragraph("Channel", table_header_style), Paragraph("# Videos", table_header_style), Paragraph("Total Niche Views", table_header_style)]]
                for c in niche_data['top_channels_in_niche'][:3]:
                    niche_channels_pdf.append([
                        Paragraph(str(c.get('title', 'N/A'))[:60], body_style),
                        Paragraph(str(c.get('niche_video_count', 0)), body_style),
                        Paragraph(f"{c.get('niche_total_views', 0):,}", body_style)
                    ])
                niche_channel_table = Table(niche_channels_pdf, colWidths=[3.5*inch, 1*inch, 2.5*inch]) # Adjusted width
                niche_channel_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.lightgrey), ('GRID', (0,0), (-1,-1), 1, colors.black)]))
                story.append(niche_channel_table)
                story.append(Spacer(1, 0.2*inch))

            if 'trending_topics' in niche_data and niche_data['trending_topics']:
                story.append(Paragraph("Trending Topics in Niche (Max 3):", styles['Normal']))
                niche_topics_pdf = [[Paragraph("Topic", table_header_style), Paragraph("# Videos", table_header_style), Paragraph("Avg Views/Video", table_header_style)]]
                for t in niche_data['trending_topics'][:3]:
                    niche_topics_pdf.append([
                        Paragraph(str(t.get('name', 'N/A'))[:60], body_style),
                        Paragraph(str(t.get('video_count', 0)), body_style),
                        Paragraph(f"{t.get('avg_views_per_video', 0):,.0f}", body_style)
                    ])
                niche_topic_table = Table(niche_topics_pdf, colWidths=[3.5*inch, 1*inch, 2.5*inch]) # Adjusted width
                niche_topic_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.lightgrey), ('GRID', (0,0), (-1,-1), 1, colors.black)]))
                story.append(niche_topic_table)
                story.append(Spacer(1, 0.2*inch))
            
            if niche_name != list(data.keys())[-1]:
                story.append(PageBreak())
            else:
                story.append(Spacer(1,0.1*inch))
    try:
        doc.build(story)
    except Exception as e:
        print(f"Error building PDF: {e}")
        buffer.seek(0)
        buffer.truncate()
        doc_error = SimpleDocTemplate(buffer, pagesize=letter)
        doc_error.build([Paragraph("Error generating PDF content due to an internal issue.", styles['Normal'])])

    buffer.seek(0)
    return buffer

def _create_bar_chart_image(data_list: List[Dict], category_key: str, value_key: str, title: str) -> Union[io.BytesIO, None]:
    """Helper to create a bar chart image using Matplotlib for PDF reports."""
    if not data_list:
        return None
    
    categories = [item.get(category_key, 'N/A') for item in data_list]
    try:
        values = [float(str(item.get(value_key, 0)).replace(',','')) for item in data_list]
    except ValueError:
        print(f"Warning: Could not convert values to float for chart: {title}")
        return None # Cannot chart non-numeric data

    if not values or not categories or len(values) != len(categories):
        return None

    fig, ax = plt.subplots(figsize=(8, 5)) # Adjusted for potentially better fit in PDF
    ax.bar(categories, values, color='skyblue')
    ax.set_ylabel('Values')
    ax.set_title(title)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    plt.close(fig) # Close the figure to free memory
    return img_buffer

def generate_report(data: Dict[str, Any], format_type: str = 'pdf', 
                   report_type: str = 'trend', include_charts: bool = True) -> Union[str, BinaryIO]:
    """
    Generate a report in the specified format
    
    Args:
        data: Dictionary containing trend analysis data
        format_type: Report format ('txt', 'csv', 'xlsx', 'pdf')
        report_type: Type of report ('trend' or 'compare')
        include_charts: Whether to include charts in PDF/Excel reports
        
    Returns:
        Report content (string for TXT/CSV, BytesIO for XLSX/PDF)
    """
    if format_type == 'txt':
        return generate_txt_report(data, report_type)
    elif format_type == 'csv':
        return generate_csv_report(data, report_type)
    elif format_type == 'xlsx':
        return generate_excel_report(data, report_type, include_charts)
    elif format_type == 'pdf':
        return generate_pdf_report(data, report_type, include_charts)
    else:
        raise ValueError(f"Unsupported format type: {format_type}")
