<?xml version = "1.0" encoding = "UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="//data">
        <html>
            <head>
                <title>Каталог магазина инструментов</title>
                <style type="text/css">
                    body {
                        font: 1.2em "Fira Sans", sans-serif;
                    }

                    .goods {
                        display: flex;
                        flex-direction:column;
                        align-items: center;
                        background-color: white;
                        max-width: 1024px;
                        margin: auto;
                        padding: 20px;
                        grid-gap: 40px;
                    }

                    .good {
                        display: flex;
                        align-items: center;
                        flex-direction:column;
                        margin: 40px
                        padding: 40px;
                        width: 100%;
                        justify-content: space-around;
                        background-color: #EEEE74;
                        border: 3px solid #CECE64;

                    }

                    h2  {
                        text-align: center;
                    }
                    img {
                        height: 300px;
                    }

                </style>
            </head>
            <body>
                <div class="goods">
                    <xsl:for-each select="//good">
                        <div class="good">
                            <h2>
                                Название:
                                <xsl:value-of select="./name"/>
                            </h2>
                            <img>
                                <xsl:attribute name="src">
                                    <xsl:value-of select="./img"/>
                                </xsl:attribute>
                            </img>
                            <span>
                                Цена
                                <xsl:value-of select="./price"/>
                                грн.
                            </span>
                            <p>
                                <h4>Описание</h4>
                                <xsl:value-of select="./description"/>
                            </p>
                        </div>
                    </xsl:for-each>
                </div>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
