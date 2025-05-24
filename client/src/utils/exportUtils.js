import jsPDF from 'jspdf';
import 'jspdf-autotable';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';

/**
 * Convert array of objects to CSV string
 * @param {Array} objArray - Array of objects to convert
 * @returns {string} CSV formatted string
 */
export const convertToCSV = (objArray) => {
  if (!objArray || !objArray.length) return '';
  
  // Get headers from the first object
  const headers = Object.keys(objArray[0]);
  
  // Add headers as first line
  let csv = headers.join(',') + '\n';
  
  // Add data rows
  objArray.forEach(item => {
    const row = headers.map(header => {
      // Handle nested objects and escape commas
      const cell = item[header];
      if (cell === null || cell === undefined) return '';
      
      // Convert objects or arrays to JSON string
      const cellValue = typeof cell === 'object' ? JSON.stringify(cell) : cell.toString();
      
      // Escape quotes and wrap in quotes if contains commas or quotes
      if (cellValue.includes(',') || cellValue.includes('"')) {
        return `"${cellValue.replace(/"/g, '""')}"`;
      }
      return cellValue;
    }).join(',');
    csv += row + '\n';
  });
  
  return csv;
};

/**
 * Create a download function for CSV data
 * @param {string} csvContent - CSV content
 * @param {string} fileName - Name of the file to download
 */
export const downloadCSV = (csvContent, fileName) => {
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  
  link.setAttribute('href', url);
  link.setAttribute('download', fileName);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

/**
 * Export video or channel data to various formats
 * @param {Object} data - Data to export
 * @param {string} type - Type of data (videos, channels)
 * @param {string} format - Export format (csv, pdf, xlsx, txt)
 */
export const exportData = (data, type, format) => {
  if (!data) return;
  
  const title = type === 'videos' ? 'YouTube Trending Videos' : 'YouTube Trending Channels';
  const fileName = `youtrend_${type}_${new Date().toISOString().split('T')[0]}`;
  
  // Flatten the data for export
  let exportData = [];
  
  if (type === 'videos') {
    exportData = data.map(video => ({
      Title: video.snippet?.title || 'No Title',
      Channel: video.snippet?.channelTitle || 'Unknown Channel',
      Views: parseInt(video.statistics?.viewCount || 0).toLocaleString(),
      Likes: parseInt(video.statistics?.likeCount || 0).toLocaleString(),
      Comments: parseInt(video.statistics?.commentCount || 0).toLocaleString(),
      Published: new Date(video.snippet?.publishedAt || Date.now()).toLocaleDateString(),
      URL: `https://www.youtube.com/watch?v=${video.id}`,
      Description: video.snippet?.description?.substring(0, 100) || 'No Description'
    }));
  } else if (type === 'channels') {
    exportData = data.map(channel => ({
      Channel: channel.snippet?.title || 'No Title',
      Subscribers: parseInt(channel.statistics?.subscriberCount || 0).toLocaleString(),
      Videos: parseInt(channel.statistics?.videoCount || 0).toLocaleString(),
      Views: parseInt(channel.statistics?.viewCount || 0).toLocaleString(),
      Country: channel.snippet?.country || 'Unknown',
      Created: new Date(channel.snippet?.publishedAt || Date.now()).toLocaleDateString(),
      URL: `https://www.youtube.com/channel/${channel.id}`,
      Description: channel.snippet?.description?.substring(0, 100) || 'No Description'
    }));
  }
  
  switch (format) {
    case 'csv':
      const csvContent = convertToCSV(exportData);
      downloadCSV(csvContent, `${fileName}.csv`);
      break;
      
    case 'xlsx':
      const worksheet = XLSX.utils.json_to_sheet(exportData);
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, type);
      XLSX.writeFile(workbook, `${fileName}.xlsx`);
      break;
      
    case 'txt':
      let txtContent = `${title}\nExport Date: ${new Date().toLocaleDateString()}\n\n`;
      
      exportData.forEach((item, index) => {
        txtContent += `Item #${index + 1}\n`;
        Object.entries(item).forEach(([key, value]) => {
          txtContent += `${key}: ${value}\n`;
        });
        txtContent += '\n';
      });
      
      const txtBlob = new Blob([txtContent], { type: 'text/plain;charset=utf-8;' });
      saveAs(txtBlob, `${fileName}.txt`);
      break;
      
    case 'pdf':
    default:
      const pdf = new jsPDF();
      
      // Add title
      pdf.setFontSize(18);
      pdf.text(title, 14, 22);
      
      // Add export date
      pdf.setFontSize(10);
      pdf.text(`Export Date: ${new Date().toLocaleDateString()}`, 14, 30);
      
      // Define table columns based on data type
      let columns = [];
      if (type === 'videos') {
        columns = [
          { header: 'Title', dataKey: 'Title' },
          { header: 'Channel', dataKey: 'Channel' },
          { header: 'Views', dataKey: 'Views' },
          { header: 'Likes', dataKey: 'Likes' },
          { header: 'Comments', dataKey: 'Comments' },
          { header: 'Published', dataKey: 'Published' }
        ];
      } else if (type === 'channels') {
        columns = [
          { header: 'Channel', dataKey: 'Channel' },
          { header: 'Subscribers', dataKey: 'Subscribers' },
          { header: 'Videos', dataKey: 'Videos' },
          { header: 'Views', dataKey: 'Views' },
          { header: 'Country', dataKey: 'Country' },
          { header: 'Created', dataKey: 'Created' }
        ];
      }
      
      // Set up auto-table
      pdf.autoTable({
        startY: 35,
        head: [columns.map(col => col.header)],
        body: exportData.map(item => columns.map(col => item[col.dataKey])),
        didDrawPage: function(data) {
          // Footer
          pdf.setFontSize(8);
          pdf.text(
            `YouTrend Report - Page ${data.pageNumber} of ${pdf.getNumberOfPages()}`,
            data.settings.margin.left,
            pdf.internal.pageSize.height - 10
          );
        }
      });
      
      // Save PDF
      pdf.save(`${fileName}.pdf`);
      break;
  }
};

/**
 * Export topics and ideas data to various formats
 * @param {Object} data - Topics and ideas data
 * @param {string} format - Export format (csv, pdf, xlsx, txt)
 */
export const exportTopicsAndIdeas = (data, format) => {
  if (!data) return;
  
  const title = 'YouTube Trending Topics & Content Ideas';
  const fileName = `youtrend_topics_ideas_${new Date().toISOString().split('T')[0]}`;
  
  const topicsData = (data.topics || []).map(topic => ({
    Topic: topic.name || 'No Name',
    Count: topic.count || 0,
    Popularity: topic.popularity || 'Unknown',
    Category: topic.category || 'General'
  }));
  
  const ideasData = (data.ideas || []).map((idea, index) => ({
    Idea: idea,
    Number: index + 1
  }));
  
  switch (format) {
    case 'csv':
      // Export topics
      if (topicsData.length > 0) {
        const topicsCsv = convertToCSV(topicsData);
        downloadCSV(topicsCsv, `${fileName}_topics.csv`);
      }
      
      // Export ideas
      if (ideasData.length > 0) {
        const ideasCsv = convertToCSV(ideasData);
        downloadCSV(ideasCsv, `${fileName}_ideas.csv`);
      }
      break;
      
    case 'xlsx':
      const workbook = XLSX.utils.book_new();
      
      // Add topics sheet
      if (topicsData.length > 0) {
        const topicsSheet = XLSX.utils.json_to_sheet(topicsData);
        XLSX.utils.book_append_sheet(workbook, topicsSheet, 'Topics');
      }
      
      // Add ideas sheet
      if (ideasData.length > 0) {
        const ideasSheet = XLSX.utils.json_to_sheet(ideasData);
        XLSX.utils.book_append_sheet(workbook, ideasSheet, 'Content Ideas');
      }
      
      XLSX.writeFile(workbook, `${fileName}.xlsx`);
      break;
      
    case 'txt':
      let txtContent = `${title}\nExport Date: ${new Date().toLocaleDateString()}\n\n`;
      
      // Add topics section
      if (topicsData.length > 0) {
        txtContent += '=== TRENDING TOPICS ===\n\n';
        topicsData.forEach((topic, index) => {
          txtContent += `Topic #${index + 1}: ${topic.Topic}\n`;
          txtContent += `Count: ${topic.Count}\n`;
          txtContent += `Popularity: ${topic.Popularity}\n`;
          txtContent += `Category: ${topic.Category}\n\n`;
        });
      }
      
      // Add ideas section
      if (ideasData.length > 0) {
        txtContent += '=== CONTENT IDEAS ===\n\n';
        ideasData.forEach(idea => {
          txtContent += `${idea.Number}. ${idea.Idea}\n\n`;
        });
      }
      
      const txtBlob = new Blob([txtContent], { type: 'text/plain;charset=utf-8;' });
      saveAs(txtBlob, `${fileName}.txt`);
      break;
      
    case 'pdf':
    default:
      const pdf = new jsPDF();
      
      // Add title
      pdf.setFontSize(18);
      pdf.text(title, 14, 22);
      
      // Add export date
      pdf.setFontSize(10);
      pdf.text(`Export Date: ${new Date().toLocaleDateString()}`, 14, 30);
      
      let yPos = 35;
      
      // Add topics section
      if (topicsData.length > 0) {
        pdf.setFontSize(14);
        pdf.text('Trending Topics', 14, yPos);
        yPos += 10;
        
        // Set up auto-table for topics
        pdf.autoTable({
          startY: yPos,
          head: [['Topic', 'Count', 'Popularity', 'Category']],
          body: topicsData.map(topic => [
            topic.Topic,
            topic.Count.toString(),
            topic.Popularity,
            topic.Category
          ]),
          didDrawPage: function(data) {
            // Footer
            pdf.setFontSize(8);
            pdf.text(
              `YouTrend Report - Page ${data.pageNumber} of ${pdf.getNumberOfPages()}`,
              data.settings.margin.left,
              pdf.internal.pageSize.height - 10
            );
          }
        });
        
        yPos = pdf.lastAutoTable.finalY + 15;
      }
      
      // Add ideas section
      if (ideasData.length > 0) {
        // Check if we need a new page
        if (yPos > 240) {
          pdf.addPage();
          yPos = 20;
        }
        
        pdf.setFontSize(14);
        pdf.text('Content Ideas', 14, yPos);
        yPos += 10;
        
        // Set up auto-table for ideas
        pdf.autoTable({
          startY: yPos,
          head: [['#', 'Content Idea']],
          body: ideasData.map(idea => [
            idea.Number.toString(),
            idea.Idea
          ])
        });
      }
      
      // Save PDF
      pdf.save(`${fileName}.pdf`);
      break;
  }
};

/**
 * Export complete data set to various formats
 * @param {Object} data - Complete data including videos, channels, topics, etc.
 * @param {string} format - Export format (csv, pdf, xlsx, txt)
 */
export const exportCompleteData = (data, format) => {
  if (!data) return;
  
  const title = 'YouTube Trend Analysis - Complete Report';
  const fileName = `youtrend_complete_report_${new Date().toISOString().split('T')[0]}`;
  
  // Prepare all data objects
  const metaData = {
    Query: data.query || 'N/A',
    Date: new Date().toLocaleDateString(),
    ResultCount: data.videos ? data.videos.length : 0,
    Country: data.country || 'Global'
  };
  
  switch (format) {
    case 'xlsx':
      const workbook = XLSX.utils.book_new();
      
      // Add metadata sheet
      const metaSheet = XLSX.utils.json_to_sheet([metaData]);
      XLSX.utils.book_append_sheet(workbook, metaSheet, 'Info');
      
      // Add videos sheet if data exists
      if (data.videos && data.videos.length > 0) {
        const videosData = data.videos.map(video => ({
          Title: video.snippet?.title || 'No Title',
          Channel: video.snippet?.channelTitle || 'Unknown Channel',
          Views: parseInt(video.statistics?.viewCount || 0).toLocaleString(),
          Likes: parseInt(video.statistics?.likeCount || 0).toLocaleString(),
          Comments: parseInt(video.statistics?.commentCount || 0).toLocaleString(),
          Published: new Date(video.snippet?.publishedAt || Date.now()).toLocaleDateString(),
          URL: `https://www.youtube.com/watch?v=${video.id}`,
          Description: video.snippet?.description?.substring(0, 100) || 'No Description'
        }));
        
        const videosSheet = XLSX.utils.json_to_sheet(videosData);
        XLSX.utils.book_append_sheet(workbook, videosSheet, 'Videos');
      }
      
      // Add channels sheet if data exists
      if (data.channels && data.channels.length > 0) {
        const channelsData = data.channels.map(channel => ({
          Channel: channel.snippet?.title || 'No Title',
          Subscribers: parseInt(channel.statistics?.subscriberCount || 0).toLocaleString(),
          Videos: parseInt(channel.statistics?.videoCount || 0).toLocaleString(),
          Views: parseInt(channel.statistics?.viewCount || 0).toLocaleString(),
          Country: channel.snippet?.country || 'Unknown',
          Created: new Date(channel.snippet?.publishedAt || Date.now()).toLocaleDateString(),
          URL: `https://www.youtube.com/channel/${channel.id}`,
          Description: channel.snippet?.description?.substring(0, 100) || 'No Description'
        }));
        
        const channelsSheet = XLSX.utils.json_to_sheet(channelsData);
        XLSX.utils.book_append_sheet(workbook, channelsSheet, 'Channels');
      }
      
      // Add topics sheet if data exists
      if (data.topics && data.topics.length > 0) {
        const topicsData = data.topics.map(topic => ({
          Topic: topic.name || 'No Name',
          Count: topic.count || 0,
          Popularity: topic.popularity || 'Unknown',
          Category: topic.category || 'General'
        }));
        
        const topicsSheet = XLSX.utils.json_to_sheet(topicsData);
        XLSX.utils.book_append_sheet(workbook, topicsSheet, 'Topics');
      }
      
      // Add ideas sheet if data exists
      if (data.ideas && data.ideas.length > 0) {
        const ideasData = data.ideas.map((idea, index) => ({
          Idea: idea,
          Number: index + 1
        }));
        
        const ideasSheet = XLSX.utils.json_to_sheet(ideasData);
        XLSX.utils.book_append_sheet(workbook, ideasSheet, 'Content Ideas');
      }
      
      XLSX.writeFile(workbook, `${fileName}.xlsx`);
      break;
      
    case 'pdf':
      const pdf = new jsPDF();
      
      // Add title
      pdf.setFontSize(20);
      pdf.text(title, 14, 22);
      
      // Add metadata
      pdf.setFontSize(12);
      pdf.text(`Query: ${metaData.Query}`, 14, 35);
      pdf.text(`Date: ${metaData.Date}`, 14, 42);
      pdf.text(`Results: ${metaData.ResultCount} videos`, 14, 49);
      pdf.text(`Country: ${metaData.Country}`, 14, 56);
      
      let yPos = 70;
      
      // Add videos section if data exists
      if (data.videos && data.videos.length > 0) {
        pdf.setFontSize(16);
        pdf.text('Top Videos', 14, yPos);
        yPos += 10;
        
        const videosData = data.videos.slice(0, 5).map(video => ({
          Title: video.snippet?.title || 'No Title',
          Channel: video.snippet?.channelTitle || 'Unknown Channel',
          Views: parseInt(video.statistics?.viewCount || 0).toLocaleString(),
          Likes: parseInt(video.statistics?.likeCount || 0).toLocaleString()
        }));
        
        pdf.autoTable({
          startY: yPos,
          head: [['Title', 'Channel', 'Views', 'Likes']],
          body: videosData.map(v => [v.Title, v.Channel, v.Views, v.Likes])
        });
        
        yPos = pdf.lastAutoTable.finalY + 15;
      }
      
      // Add channels section if data exists
      if (data.channels && data.channels.length > 0) {
        // Check if we need a new page
        if (yPos > 200) {
          pdf.addPage();
          yPos = 20;
        }
        
        pdf.setFontSize(16);
        pdf.text('Top Channels', 14, yPos);
        yPos += 10;
        
        const channelsData = data.channels.slice(0, 5).map(channel => ({
          Channel: channel.snippet?.title || 'No Title',
          Subscribers: parseInt(channel.statistics?.subscriberCount || 0).toLocaleString(),
          Videos: parseInt(channel.statistics?.videoCount || 0).toLocaleString()
        }));
        
        pdf.autoTable({
          startY: yPos,
          head: [['Channel', 'Subscribers', 'Videos']],
          body: channelsData.map(c => [c.Channel, c.Subscribers, c.Videos])
        });
        
        yPos = pdf.lastAutoTable.finalY + 15;
      }
      
      // Add topics section if data exists
      if (data.topics && data.topics.length > 0) {
        // Check if we need a new page
        if (yPos > 200) {
          pdf.addPage();
          yPos = 20;
        }
        
        pdf.setFontSize(16);
        pdf.text('Trending Topics', 14, yPos);
        yPos += 10;
        
        const topicsData = data.topics.map(topic => [
          topic.name || 'No Name',
          topic.count?.toString() || '0'
        ]);
        
        pdf.autoTable({
          startY: yPos,
          head: [['Topic', 'Count']],
          body: topicsData
        });
        
        yPos = pdf.lastAutoTable.finalY + 15;
      }
      
      // Add ideas section if data exists
      if (data.ideas && data.ideas.length > 0) {
        // Always start ideas on a new page
        pdf.addPage();
        
        pdf.setFontSize(16);
        pdf.text('Content Ideas', 14, 20);
        
        pdf.autoTable({
          startY: 30,
          head: [['#', 'Content Idea']],
          body: data.ideas.map((idea, idx) => [
            (idx + 1).toString(),
            idea
          ])
        });
      }
      
      // Add footer to all pages
      const pageCount = pdf.internal.getNumberOfPages();
      for (let i = 1; i <= pageCount; i++) {
        pdf.setPage(i);
        pdf.setFontSize(8);
        pdf.text(
          `YouTrend Complete Report - Page ${i} of ${pageCount}`,
          14,
          pdf.internal.pageSize.height - 10
        );
      }
      
      pdf.save(`${fileName}.pdf`);
      break;
      
    case 'txt':
      let txtContent = `${title}\n`;
      txtContent += `===========================================\n\n`;
      
      // Add metadata
      txtContent += `REPORT INFORMATION\n`;
      txtContent += `------------------\n`;
      txtContent += `Query: ${metaData.Query}\n`;
      txtContent += `Date: ${metaData.Date}\n`;
      txtContent += `Results: ${metaData.ResultCount} videos\n`;
      txtContent += `Country: ${metaData.Country}\n\n`;
      
      // Add videos section if data exists
      if (data.videos && data.videos.length > 0) {
        txtContent += `TOP VIDEOS\n`;
        txtContent += `----------\n\n`;
        
        data.videos.slice(0, 10).forEach((video, idx) => {
          txtContent += `${idx + 1}. ${video.snippet?.title || 'No Title'}\n`;
          txtContent += `   Channel: ${video.snippet?.channelTitle || 'Unknown Channel'}\n`;
          txtContent += `   Views: ${parseInt(video.statistics?.viewCount || 0).toLocaleString()}\n`;
          txtContent += `   Likes: ${parseInt(video.statistics?.likeCount || 0).toLocaleString()}\n`;
          txtContent += `   URL: https://www.youtube.com/watch?v=${video.id}\n\n`;
        });
      }
      
      // Add channels section if data exists
      if (data.channels && data.channels.length > 0) {
        txtContent += `TOP CHANNELS\n`;
        txtContent += `-----------\n\n`;
        
        data.channels.slice(0, 10).forEach((channel, idx) => {
          txtContent += `${idx + 1}. ${channel.snippet?.title || 'No Title'}\n`;
          txtContent += `   Subscribers: ${parseInt(channel.statistics?.subscriberCount || 0).toLocaleString()}\n`;
          txtContent += `   Videos: ${parseInt(channel.statistics?.videoCount || 0).toLocaleString()}\n`;
          txtContent += `   URL: https://www.youtube.com/channel/${channel.id}\n\n`;
        });
      }
      
      // Add topics section if data exists
      if (data.topics && data.topics.length > 0) {
        txtContent += `TRENDING TOPICS\n`;
        txtContent += `---------------\n\n`;
        
        data.topics.forEach((topic, idx) => {
          txtContent += `${idx + 1}. ${topic.name || 'No Name'} (Count: ${topic.count || 0})\n`;
        });
        txtContent += '\n';
      }
      
      // Add ideas section if data exists
      if (data.ideas && data.ideas.length > 0) {
        txtContent += `CONTENT IDEAS\n`;
        txtContent += `-------------\n\n`;
        
        data.ideas.forEach((idea, idx) => {
          txtContent += `${idx + 1}. ${idea}\n\n`;
        });
      }
      
      // Add footer
      txtContent += `===========================================\n`;
      txtContent += `Generated by YouTrend - ${new Date().toLocaleString()}\n`;
      
      const txtBlob = new Blob([txtContent], { type: 'text/plain;charset=utf-8;' });
      saveAs(txtBlob, `${fileName}.txt`);
      break;
      
    case 'csv':
    default:
      // For CSV, export multiple files since we can't have multiple sheets
      
      // Export metadata
      const metaDataCsv = convertToCSV([metaData]);
      downloadCSV(metaDataCsv, `${fileName}_info.csv`);
      
      // Export videos if data exists
      if (data.videos && data.videos.length > 0) {
        const videosData = data.videos.map(video => ({
          Title: video.snippet?.title || 'No Title',
          Channel: video.snippet?.channelTitle || 'Unknown Channel',
          Views: parseInt(video.statistics?.viewCount || 0).toLocaleString(),
          Likes: parseInt(video.statistics?.likeCount || 0).toLocaleString(),
          Comments: parseInt(video.statistics?.commentCount || 0).toLocaleString(),
          Published: new Date(video.snippet?.publishedAt || Date.now()).toLocaleDateString(),
          URL: `https://www.youtube.com/watch?v=${video.id}`
        }));
        
        const videosCsv = convertToCSV(videosData);
        downloadCSV(videosCsv, `${fileName}_videos.csv`);
      }
      
      // Export channels if data exists
      if (data.channels && data.channels.length > 0) {
        const channelsData = data.channels.map(channel => ({
          Channel: channel.snippet?.title || 'No Title',
          Subscribers: parseInt(channel.statistics?.subscriberCount || 0).toLocaleString(),
          Videos: parseInt(channel.statistics?.videoCount || 0).toLocaleString(),
          Views: parseInt(channel.statistics?.viewCount || 0).toLocaleString(),
          URL: `https://www.youtube.com/channel/${channel.id}`
        }));
        
        const channelsCsv = convertToCSV(channelsData);
        downloadCSV(channelsCsv, `${fileName}_channels.csv`);
      }
      
      // Export topics if data exists
      if (data.topics && data.topics.length > 0) {
        const topicsData = data.topics.map(topic => ({
          Topic: topic.name || 'No Name',
          Count: topic.count || 0
        }));
        
        const topicsCsv = convertToCSV(topicsData);
        downloadCSV(topicsCsv, `${fileName}_topics.csv`);
      }
      
      // Export ideas if data exists
      if (data.ideas && data.ideas.length > 0) {
        const ideasData = data.ideas.map((idea, index) => ({
          Number: index + 1,
          Idea: idea
        }));
        
        const ideasCsv = convertToCSV(ideasData);
        downloadCSV(ideasCsv, `${fileName}_ideas.csv`);
      }
      break;
  }
};
