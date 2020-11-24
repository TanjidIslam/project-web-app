/**
 * Created by Tanjid Islam on 30/04/2016.
 */
$(function () {
    var selectForm = new Array();
    selectForm["username-option"] = "#userAdvanced";
    selectForm["user-option"] = "#usersAdvanced";
    selectForm["repo-option"] = "#repoAdvanced";
    selectForm["code-option"] = "#codeAdvanced";
    selectForm["issue-option"] = "#issueAdvanced";

    var listFields = ["#userAdvanced", "#usersAdvanced", "#repoAdvanced", "#codeAdvanced", "#issueAdvanced"];

    $("#searchCategory").change(function () {
        //noinspection JSValidateTypes
        var field = $(this).children(":selected").attr("id");
        console.log(field);
        for (var i = 0; i < listFields.length; i++) {
            if(listFields[i] != selectForm[field]){
                $(listFields[i]).hide();
            } else {
                $(listFields[i]).show();
            }
        }
    }).trigger('change');
});