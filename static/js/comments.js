axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

let app = new Vue({
    el: '#app',
    data() {
        return {
            pageUrl: null,
            product: null,
            comments: null,
            newComment: null,
            actualComment: null,
            newText: null,
            error: null
        }
    },
    mounted() {
        this.pageUrl = new URL(window.location.href);
        this.product = /^(\/product\/)(\d+)(\/comments)/.exec(this.pageUrl.pathname)[2];
        let url = '/api/products/' + this.product + '/comments-list/'
        axios.get(url)
            .then(response => {
                if (response.status === 200) {
                    this.comments = response.data
                } else {
                    this.error = "Evènement inattendu lors de la " +
                        "récupération des commentaires : " + response.status + " " + response.statusText
                }

            })
            .catch((error) => {
                this.error = "Erreur lors de la " +
                    "récupération des commentaires : " + error.response.status + " " + error.response.statusText
            })
    },
    methods: {
        // test if user can update comment
        canUpdate: function (comment) {
            for (let i = 0; i < comment.permissions.length; i++) {
                if (comment.permissions[i] === 'can_change_all_commments') {
                    return true
                }
            }
            return false
        },

        // test if user can delete comment
        canDelete: function (comment) {
            for (let i = 0; i < comment.permissions.length; i++) {
                if (comment.permissions[i] === 'can_delete_all_comments') {
                    return true
                }
            }
            return false
        },


        // create comment
        createComment: function (text) {
            url = '/api/comments/'
            axios.post(url, {'comment_text': text, 'product': this.product}).then((response => {
                    if (response.status < 300) {
                        this.comments.unshift(response.data);
                        this.newComment = null
                    } else {
                        this.error = "Evènement inattendu lors de la " +
                            "création d'un commentaire : " + response.status + " " + response.statusText
                    }
                })
            ).catch(function (error) {
                this.error = "Erreur lors de la " +
                    "création d'un commentaire : " + error.response.status + " " + error.response.statusText
            })
        },
        // display comment's update form
        displayUpdateForm: function (comment) {
            if (this.actualComment !== comment) {
                this.actualComment = comment
            } else {
                this.actualComment = null
            }
        },

        // update comment text
        updateComment: function (comment) {
            url = '/api/comments/' + this.actualComment.pk + '/'
            axios.patch(url, {'comment_text': this.actualComment.comment_text}).then((response => {
                    if (response.status < 300) {
                        this.actualComment = null
                    } else {
                        this.error = "Evènement inattendu lors de la " +
                            "mise à jour d'un commentaire : " + response.status + " " + response.statusText
                    }

                })
            ).catch(function (error) {
                console.error(error);
                this.error = "Erreur lors de la " +
                    "mise à jour des commentaires : " + error.response.status + " " + error.response.statusText
            })
        },
        // delete of a comment
        deleteComment: function (pk) {
            comments = this.comments
            let url = '/api/comments/' + pk;
            axios.delete(url).then((response) => {
                if (response.status < 300) {
                    this.comments = comments.filter(function (value, index, arr) {
                        return value.pk !== pk;
                    })
                } else {
                    this.error = "Evènement inattendu lors de la " +
                    "suppression d'un commentaire : " + response.status + " " + response.statusText
                }
            }).catch(function (error) {
                console.error(error);
                this.error = "Erreur lors de la " +
                    "suppression des commentaires : " + error.response.status + " " + error.response.statusText
            })
        }
    },
    filters: {
        frenchDate: function (value) {
            if (!value) return ''
            return  moment(value).format('DD/MM/YYYY à HH:mm:ss');
        }
    }
});