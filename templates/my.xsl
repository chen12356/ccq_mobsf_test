<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:outline="http://wkhtmltopdf.org/outline"
                xmlns="http://www.w3.org/1999/xhtml">
    <xsl:output doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
                doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitiona
l.dtd"
                indent="yes" />
    <xsl:template match="outline:outline">
        <html>
            <head>
                <title>目录</title>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
                <style>
                    h3 {
                        font-family: 'Microsoft YaHei UI';
                        font-size: 40pt;
                        width: 100%;
                        border-bottom: 1px solid;
                        margin-bottom: 0.5rem;
                        font-weight: 500;
                        line-height: 1.2;
                        color: inherit;
                        margin-top: 0;
                        margin-bottom: 0.5rem;
                        color: rgb(0,109,85);
                        font-weight:bold;
                    }
                    div {border-bottom: 1px dashed rgb(200,200,200);}
                    span {float: right;}
                    li {list-style: none;}
                    ul {
                        font-size: 20px;
                        font-family: 'Microsoft YaHei UI';
                        padding:2px;
                    }
                    ul ul {font-size: 70%; }
                    ul {padding-left: 0em;}
                    ul ul {padding-left: 1em;}
                    a {text-decoration:none; color: black;}
                    .container{
                        padding-top:40px;
                        padding-left:15px;
                        padding-right:15px;
                    }

                </style>
            </head>
            <body>
                <div class="container">
                    <h3>Table of Contents</h3>
                    <ul ><xsl:apply-templates select="outline:item/outline:item"/></ul>
                </div>

            </body>
        </html>
    </xsl:template>


    <xsl:template match="outline:item">
        <li>
            <xsl:if test="(@title!='') and (@title!='Table of Contents')">
                <div>
                    <a>
                        <xsl:if test="@link">
                            <xsl:attribute name="href"><xsl:value-of select="@link"/></xsl:attribute>
                        </xsl:if>
                        <xsl:if test="@backLink">
                            <xsl:attribute name="name"><xsl:value-of select="@backLink"/></xsl:attribute>
                        </xsl:if>
                        <xsl:value-of select="@title" />
                    </a>
                    <span> <xsl:value-of select="@page" /> </span>
                </div>
            </xsl:if>
            <ul>
                <xsl:comment>added to prevent self-closing tags in QtXmlPatterns</xsl:comment>
                <xsl:apply-templates select="outline:item"/>
            </ul>
        </li>
    </xsl:template>
</xsl:stylesheet>


