<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output method="html" indent="yes" encoding="UTF-8"/>
<!--  Key to look up station names by id  -->
<xsl:key name="station-by-id" match="station" use="@id"/>
<xsl:template match="/">
<html>
<head>
<title>Train Trips Report</title>
<style> body { font-family: Arial, sans-serif; margin: 20px; background: #f0f2f5; } h1 { color: #2c3e50; text-align: center; border-bottom: 3px solid #3498db; padding-bottom: 10px; } .line { background: white; margin: 20px 0; padding: 15px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); } .line h2 { color: #2980b9; border-bottom: 1px solid #ecf0f1; padding-bottom: 8px; } .trips-label { font-weight: bold; color: #c0392b; margin: 10px 0 5px 0; } .trip { margin: 15px 0; padding: 10px; border-left: 4px solid #3498db; background: #fafafa; } .trip h3 { margin: 0 0 6px 0; font-size: 14px; color: #333; } table { width: 100%; border-collapse: collapse; margin-top: 8px; } th, td { border: 1px solid #ddd; padding: 8px; text-align: center; } th { background: #3498db; color: white; } td.vip { color: #e67e22; font-weight: bold; } .days { font-size: 12px; color: #7f8c8d; margin-top: 5px; } </style>
</head>
<body>
<h1>🚆 Train Trips Report</h1>
<xsl:for-each select="transport/lines/line">
<xsl:variable name="dep-id" select="@departure"/>
<xsl:variable name="arr-id" select="@arrival"/>
<xsl:variable name="dep-name" select="key('station-by-id', $dep-id)/@name"/>
<xsl:variable name="arr-name" select="key('station-by-id', $arr-id)/@name"/>
<div class="line">
<h2>
Line:
<xsl:value-of select="@code"/>
(
<xsl:value-of select="$dep-name"/>
→
<xsl:value-of select="$arr-name"/>
)
</h2>
<p class="trips-label">Detailed List of Trips:</p>
<xsl:for-each select="trips/trip">
<xsl:variable name="sched" select="schedule"/>
<div class="trip">
<h3>
Trip No.
<xsl:value-of select="@code"/>
: departureure:
<xsl:value-of select="$dep-name"/>
| Arrival:
<xsl:value-of select="$arr-name"/>
</h3>
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
<xsl:for-each select="class">
<tr>
<td>
<xsl:value-of select="$sched/@departure"/>
 - 
<xsl:value-of select="$sched/@arrival"/>
</td>
<td>
<xsl:value-of select="../@type"/>
</td>
<td>
<xsl:choose>
<xsl:when test="@type='VIP'">
<span style="color:#e67e22;font-weight:bold;">VIP</span>
</xsl:when>
<xsl:otherwise>
<xsl:value-of select="@type"/>
</xsl:otherwise>
</xsl:choose>
</td>
<td>
<xsl:choose>
<xsl:when test="@type='VIP'">
<span style="color:#e67e22;font-weight:bold;">
<xsl:value-of select="@price"/>
</span>
</xsl:when>
<xsl:otherwise>
<xsl:value-of select="@price"/>
</xsl:otherwise>
</xsl:choose>
</td>
</tr>
</xsl:for-each>
</tbody>
</table>
<p class="days">
📅 Days:
<xsl:value-of select="days"/>
</p>
</div>
</xsl:for-each>
</div>
</xsl:for-each>
</body>
</html>
</xsl:template>
</xsl:stylesheet>