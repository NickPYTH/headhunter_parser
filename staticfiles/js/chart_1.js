alert("type");

var oilCanvas = document.getElementById("oilChart");

        lst = [];
        lst_val = [];
        for (i = 1; i < 11; i++){
            lst[i] = document.getElementById(i).textContent;
        }

        for (i = 1; i < 11; i++){
            lst_val[i] = document.getElementById(i+"_value").textContent;
        }

        Chart.defaults.global.defaultFontFamily = "Comfortaa";
        Chart.defaults.global.defaultFontSize = 18;

        var oilData = {
            labels: [
                lst[1],
                lst[2],
                lst[3],
                lst[4],
                lst[5],
                lst[6],
                lst[7],
                lst[8],
                lst[9],
                lst[10],
            ],
            datasets: [
                {
                    data: [
                        lst_val[1],
                        lst_val[2],
                        lst_val[3],
                        lst_val[4],
                        lst_val[5],
                        lst_val[6],
                        lst_val[7],
                        lst_val[8],
                        lst_val[9],
                        lst_val[10],
                    ],
                    backgroundColor: [
                        "#1E90FF",
                        "#696969",
                        "#84FF63",
                        "#8463FF",
                        "#6384FF",
                        "#00FFFF",
                        "#63FF84",
                        "#FF00FF",
                        "#FFFF00",
                        "#00FF00"
                    ]
                }]
        };

        var pieChart = new Chart(oilCanvas, {
        type: 'pie',
        data: oilData
        });