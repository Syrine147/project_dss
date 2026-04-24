<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:math="http://www.w3.org/2005/xpath-functions/math"
    exclude-result-prefixes="xs math"
    version="1.0">
   
        
        <xsl:output method="html" indent="yes" encoding="UTF-8"/>
        
        <xsl:template match="/">
            <html>
                <head>
                    <title>Train Trips Report</title>
                    <style>
                        body {
                        font-family: Arial, sans-serif;
                        margin: 20px;
                        background: #f0f2f5;
                        }
                        h1 {
                        color: #2c3e50;
                        text-align: center;
                        }
                        .line {
                        background: white;
                        margin: 20px 0;
                        padding: 15px;
                        border-radius: 8px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        }
                        .trip {
                        margin: 15px 0;
                        padding: 10px;
                        border-left: 4px solid #3498db;
                        background: #fafafa;
                        }
                        table {
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 10px;
                        }
                        th, td {
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                        }
                        th {
                        background: #3498db;
                        color: white;
                        }
                    </style>
                </head>
                <body>
                    <h1>🚆 Train Trips Report</h1>
                    <xsl:for-each select="transport/line">
                        <div class="line">
                            <h2>Line: <xsl:value-of select="@code"/> 
                                (<xsl:value-of select="@cityDepart"/> → <xsl:value-of select="@cityArrival"/>)
                            </h2>
                            
                            <xsl:for-each select="trip">
                                <div class="trip">
                                    <h3>Trip No. <xsl:value-of select="@number"/></h3>
                                    <p>Departure: <xsl:value-of select="../@cityDepart"/> | 
                                        Arrival: <xsl:value-of select="../@cityArrival"/></p>
                                    
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>Schedule</th>
                                                <th>Train Type</th>
                                                <th>Class</th>
                                                <th>Price (DA)</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <xsl:for-each select="schedule">
                                                <tr>
                                                    <td><xsl:value-of select="@departureTime"/> - <xsl:value-of select="@arrivalTime"/></td>
                                                    <td><xsl:value-of select="trainType"/></td>
                                                    <td><xsl:value-of select="class"/></td>
                                                    <td><xsl:value-of select="price"/></td>
                                                </tr>
                                            </xsl:for-each>
                                        </tbody>
                                    </table>
                                </div>
                            </xsl:for-each>
                        </div>
                    </xsl:for-each>
                    
                </body>
            </html>
        </xsl:template>
</xsl:stylesheet>